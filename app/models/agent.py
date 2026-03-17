from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Agent(Base, TimestampMixin):
    """Agent model"""
    __tablename__ = "agent"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=True)

    # JSON string
    allowed_tools: Mapped[str] = mapped_column(Text, nullable=True)
    allowed_kbs: Mapped[str] = mapped_column(Text, nullable=True)
    chat_options: Mapped[str] = mapped_column(Text, nullable=True)
