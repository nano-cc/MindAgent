from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ChatMessage(Base, TimestampMixin):
    """Chat message model"""
    __tablename__ = "chat_message"

    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, assistant, tool, system
    content: Mapped[str] = mapped_column(Text, nullable=True)
    metadata: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
