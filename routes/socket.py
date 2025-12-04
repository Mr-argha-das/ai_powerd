from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Optional
from sqlalchemy.orm import Session
from db.database import get_db
from models.messages import ConversationMatrimonies, MessageMatrimonies
from models.userModels import MatrimoniesUser
import random
import string
import traceback

router = APIRouter(tags=["matrimonies"])

# ---------------------------
# GENERATE RANDOM MESSAGE ID
# ---------------------------
def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# ============================================================
#           CHAT CONNECTION MANAGER
# ============================================================
class ChatConnectionManager:
    def __init__(self):
        # use string keys for user ids
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[str(user_id)] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(str(user_id), None)

    async def send_message(self, user_id: str, payload: dict):
        socket = self.active_connections.get(str(user_id))
        if socket:
            try:
                await socket.send_json(payload)
            except Exception:
                # don't let one failing socket crash server
                traceback.print_exc()


chat_manager = ChatConnectionManager()


# ============================================================
#           INBOX CONNECTION MANAGER
# ============================================================
class InboxConnectionManager:
    def __init__(self):
        self.inbox_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.inbox_connections[str(user_id)] = websocket

    def disconnect(self, user_id: str):
        self.inbox_connections.pop(str(user_id), None)

    async def send_inbox(self, user_id: str, inbox_data: list):
        ws = self.inbox_connections.get(str(user_id))
        if ws:
            try:
                await ws.send_json({
                    "event": "inbox_update",
                    "inbox": inbox_data
                })
            except Exception:
                traceback.print_exc()


inbox_manager = InboxConnectionManager()


# ============================================================
#           BUILD INBOX (USED IN MULTIPLE PLACES)
# ============================================================
def _safe_user_field(user: Optional[MatrimoniesUser], field_name: str, fallback=None):
    if not user:
        return fallback
    return getattr(user, field_name, fallback)


def build_inbox(db: Session, user_id: str):
    # Ensure numeric comparison uses int
    try:
        uid_int = int(user_id)
    except Exception:
        uid_int = user_id  # fallback, though ideally user_id should be int-able

    conversations = db.query(ConversationMatrimonies).filter(
        (ConversationMatrimonies.user1_id == uid_int) |
        (ConversationMatrimonies.user2_id == uid_int)
    ).all()

    inbox_list = []

    for convo in conversations:
        # determine other user id safely
        try:
            other_id = convo.user2_id if convo.user1_id == uid_int else convo.user1_id
        except Exception:
            # fallback if values are unexpected
            other_id = convo.user2_id or convo.user1_id

        other_user = db.query(MatrimoniesUser).get(other_id)
        last_msg = None
        if convo.last_message_id:
            last_msg = db.query(MessageMatrimonies).get(convo.last_message_id)

        # timestamp must be JSON serializable -> convert to isoformat string or None
        ts = None
        if last_msg and getattr(last_msg, "timestamp", None):
            try:
                ts = last_msg.timestamp.isoformat()
            except Exception:
                ts = str(last_msg.timestamp)

        inbox_list.append({
            "conversation_id": str(convo.id),
            "other_user": {
                "_id": str(_safe_user_field(other_user, "id", "")),
                "name": _safe_user_field(other_user, "name", ""),
                "profilePick": _safe_user_field(other_user, "profile_photo", ""),
                "is_readed": bool(last_msg.is_read) if last_msg and getattr(last_msg, "is_read", None) is not None else False,
                "sender_you": True if last_msg and int(last_msg.sender_id) == uid_int else False
            },
            "last_message": last_msg.message if last_msg and getattr(last_msg, "message", None) is not None else "",
            "timestamp": ts
        })

    return inbox_list


# ============================================================
#                   SEND MESSAGE + UPDATE CONVO
# ============================================================
async def save_and_push_message(sender_id, receiver_id, message, db: Session):
    # normalize ids to ints where possible
    try:
        s_id = int(sender_id)
    except Exception:
        s_id = sender_id

    try:
        r_id = int(receiver_id)
    except Exception:
        r_id = receiver_id

    # 1. Save message
    msg = MessageMatrimonies(
        sender_id=s_id,
        receiver_id=r_id,
        message=message
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # 2. Update conversation
    convo = db.query(ConversationMatrimonies).filter(
        ((ConversationMatrimonies.user1_id == s_id) & (ConversationMatrimonies.user2_id == r_id)) |
        ((ConversationMatrimonies.user1_id == r_id) & (ConversationMatrimonies.user2_id == s_id))
    ).first()

    if not convo:
        convo = ConversationMatrimonies(
            user1_id=s_id,
            user2_id=r_id,
            last_message_id=msg.id
        )
        db.add(convo)
    else:
        convo.last_message_id = msg.id

    db.commit()

    # 3. Push CHAT message to receiver (if connected)
    chat_payload = {
        "id": generate_random_string(),
        "sender_id": str(s_id),
        "message": message,
        "timestamp": msg.timestamp.isoformat() if getattr(msg, "timestamp", None) else None
    }
    await chat_manager.send_message(str(r_id), chat_payload)

    # 4. Build inbox for both (strings)
    sender_inbox = build_inbox(db, str(s_id))
    receiver_inbox = build_inbox(db, str(r_id))

    # 5. Push inbox to BOTH users (wrapped in try/except inside manager)
    await inbox_manager.send_inbox(str(s_id), sender_inbox)
    await inbox_manager.send_inbox(str(r_id), receiver_inbox)


# ============================================================
#                  CHAT WEBSOCKET ROUTE
# ============================================================
@router.websocket("/matrimonies/chat/ws/{user_id}")
async def chat_websocket(websocket: WebSocket, user_id: str):
    # create DB session (your original pattern)
    db: Session = next(get_db())
    await chat_manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()

            receiver_id = data.get("receiver_id")
            
            message = data.get("message")

            if not receiver_id or not message:
                await websocket.send_json({"error": "receiver_id or message missing"})
                continue

            await save_and_push_message(user_id, receiver_id, message, db)

    except WebSocketDisconnect:
        chat_manager.disconnect(user_id)
    except Exception:
        traceback.print_exc()
        chat_manager.disconnect(user_id)


# ============================================================
#                  INBOX WEBSOCKET ROUTE
# ============================================================
@router.websocket("/matrimonies/inbox/ws/{user_id}")
async def inbox_websocket(websocket: WebSocket, user_id: str):
    db: Session = next(get_db())
    await inbox_manager.connect(websocket, user_id)

    # Initial inbox send (when socket connects)
    try:
        initial_inbox = build_inbox(db, user_id)
        await inbox_manager.send_inbox(user_id, initial_inbox)
    except Exception:
        # if initial send fails, log but keep socket open
        traceback.print_exc()

    try:
        while True:
            # keep the connection open; client can optionally send pings/pongs or simple text
            await websocket.receive_text()

    except WebSocketDisconnect:
        inbox_manager.disconnect(user_id)
    except Exception:
        traceback.print_exc()
        inbox_manager.disconnect(user_id)
