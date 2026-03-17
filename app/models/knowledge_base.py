from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class KnowledgeBase(Base, TimestampMixin):
    """Knowledge base model"""
    __tablename__ = "knowledge_base"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    metadata: Mapped[str] = mapped_column(Text, nullable=True)
