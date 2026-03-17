from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    """Document model"""
    __tablename__ = "document"

    kb_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filetype: Mapped[str] = mapped_column(String(100), nullable=True)
    size: Mapped[int] = mapped_column(BigInteger, nullable=True)
    metadata: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
