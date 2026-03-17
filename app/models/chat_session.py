from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    """Chat session model"""
    __tablename__ = "chat_session"

    agent_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    metadata: Mapped[str] = mapped_column(Text, nullable=True)
