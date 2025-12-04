from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
# from models.messages import Conversation, Message
from models.messages import ConversationMatrimonies, MessageMatrimonies
from models.userModels import MatrimoniesUser

router = APIRouter(tags=["matrimonies"])

@router.get("/matrimonies/chats/inbox/{user_id}")
async def get_inbox(user_id: str, db: Session = Depends(get_db)):
    selfUser = db.query(MatrimoniesUser).get(int(user_id))
    conversations = db.query(ConversationMatrimonies).filter(
        (ConversationMatrimonies.user1_id == user_id) | (ConversationMatrimonies.user2_id == user_id)
    ).all()
    inbox_list = []

    if not conversations:
        return {"message": "Here is all Conversation", "inbox": inbox_list, "status": 200}

    
    for convo in conversations:
        last_message_text = ""
        other_user_id = ""
        if int(user_id) == convo.user1_id:
            other_user_id = convo.user2_id
            print("pass1")
        elif int(user_id) == convo.user2_id:
            print("pass2")
            other_user_id = convo.user1_id
        print("================================")
        print(f"user id: {other_user_id}")
        user = db.query(MatrimoniesUser).get(other_user_id)
        print(user)

        last_msg = db.query(MessageMatrimonies).get(convo.last_message_id)
        if last_msg:
            if int(last_msg.sender_id) == int(user_id):
                # last_message_text = "seen just now" if last_msg.is_read else "Sent just now"
                last_message_text = "Message seen" if last_msg.is_read == True else "Message sent's"
            else:
                last_message_text = last_msg.message
        else:
            last_message_text = ""

        inbox_list.append({
            "conversation_id": convo.id,
            "other_user": {
                "_id": user.id,
                "name": user.name,
                "profilePick": user.profile_photo,
                "is_readed": last_msg.is_read if last_msg else False,
                "sender_you": True if last_msg and int(last_msg.sender_id) == int(user_id) else False
            },
            "last_message": last_message_text,
            "timestamp": last_msg.timestamp if last_msg else None
        })

    return {"@message": "Here is all Conversation", "@inbox": inbox_list,"@eged_user": selfUser, "@status": 200, }


@router.get("/matrimonies/chats/history/{user1}/{user2}")
async def get_chat_history(user1: str, user2: str, db: Session = Depends(get_db)):
    messages = db.query(MessageMatrimonies).filter(
        ((MessageMatrimonies.sender_id == user1) & (MessageMatrimonies.receiver_id == user2)) |
        ((MessageMatrimonies.sender_id == user2) & (MessageMatrimonies.receiver_id == user1))
    ).order_by(MessageMatrimonies.timestamp.asc()).all()

    return {
        "message": "All chats",
        "chat": [
            {"sender": msg.sender_id, "message": msg.message, "timestamp": msg.timestamp}
            for msg in messages
        ],
        "status": 200
    }


@router.post("/matrimonies/chats/mark_seen/{conversation_id}/{user_id}")
async def mark_messages_as_seen(conversation_id: str, user_id: str, db: Session = Depends(get_db)):
    conversation = db.query(ConversationMatrimonies).get(conversation_id)

    if not conversation or (int(user_id) not in [conversation.user1_id, conversation.user2_id]):
        raise HTTPException(status_code=403, detail="Not authorized to access this chat.")

    db.query(MessageMatrimonies).filter(
        MessageMatrimonies.receiver_id == user_id,
        MessageMatrimonies.sender_id.in_([conversation.user1_id, conversation.user2_id]),
        MessageMatrimonies.is_read == False
    ).update({"is_read": True})
    db.commit()

    last_msg = db.query(MessageMatrimonies).get(conversation.last_message_id)
    if last_msg and last_msg.receiver_id == user_id:
        last_msg.is_read = True
        db.commit()

    return {"message": "Messages marked as seen", "status": 200}


@router.get("/matrimonies/matrimonies")
def get_all_customers(db: Session = Depends(get_db)):
    customers = db.query(MatrimoniesUser).all()
    return {
        "message":"here es this all matrimonies user",
        "data":customers
    }