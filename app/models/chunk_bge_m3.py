from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ChunkBgeM3(Base, TimestampMixin):
    """Vector chunk model for BGE-M3 embeddings"""
    __tablename__ = "chunk_bge_m3"

    kb_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    doc_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Store as JSON array of floats
    embedding: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
