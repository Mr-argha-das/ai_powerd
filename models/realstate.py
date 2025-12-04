from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT
from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Enum, TIMESTAMP
)
from sqlalchemy.sql import func
import uuid

from db.database import Base


class MessageRealState(Base):
    __tablename__ = "messages_table_RealState"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    sender_id = Column(BIGINT(unsigned=True), ForeignKey("real_estate_users.id"), nullable=False)
    receiver_id = Column(BIGINT(unsigned=True), ForeignKey("real_estate_users.id"), nullable=False)

    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    sender = relationship("UserRealState", foreign_keys=[sender_id])
    receiver = relationship("UserRealState", foreign_keys=[receiver_id])

class ConversationRealState(Base):
    __tablename__ = "conversations_RealState"
# 
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user1_id = Column(BIGINT(unsigned=True), ForeignKey("real_estate_users.id"), nullable=False)
    user2_id = Column(BIGINT(unsigned=True), ForeignKey("real_estate_users.id"), nullable=False)

    last_message_id = Column(String(36), ForeignKey("messages_table_RealState.id"))

    last_message = relationship("MessageRealState", foreign_keys=[last_message_id])

class UserRealState(Base):
    __tablename__ = "real_estate_users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    role = Column(
        Enum('buyer', 'agent', name='user_role_enum'),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )

    status = Column(String(255), default="pending", nullable=False)