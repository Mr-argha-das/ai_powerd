from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT
from datetime import datetime
import uuid

from db.database import Base


class MessageMatrimonies(Base):
    __tablename__ = "messages_table_matrimonies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    sender_id = Column(BIGINT(unsigned=True), ForeignKey("matrimonies.id"), nullable=False)
    receiver_id = Column(BIGINT(unsigned=True), ForeignKey("matrimonies.id"), nullable=False)

    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    sender = relationship("MatrimoniesUser", foreign_keys=[sender_id])
    receiver = relationship("MatrimoniesUser", foreign_keys=[receiver_id])

class ConversationMatrimonies(Base):
    __tablename__ = "conversations_matrimonies"
# 
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user1_id = Column(BIGINT(unsigned=True), ForeignKey("matrimonies.id"), nullable=False)
    user2_id = Column(BIGINT(unsigned=True), ForeignKey("matrimonies.id"), nullable=False)

    last_message_id = Column(String(36), ForeignKey("messages_table_matrimonies.id"))

    last_message = relationship("MessageMatrimonies", foreign_keys=[last_message_id])