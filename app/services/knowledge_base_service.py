from typing import List, Optional
from datetime import datetime
import json

from app.models import KnowledgeBase
from app.database import Session


class KnowledgeBaseService:
    """Knowledge base service for CRUD operations"""

    @staticmethod
    def get_all() -> List[KnowledgeBase]:
        """Get all knowledge bases"""
        with Session() as db:
            return db.query(KnowledgeBase).all()

    @staticmethod
    def get_by_id(kb_id: str) -> Optional[KnowledgeBase]:
        """Get knowledge base by ID"""
        with Session() as db:
            return db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()

    @staticmethod
    def create(
        name: str,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> KnowledgeBase:
        """Create new knowledge base"""
        with Session() as db:
            kb = KnowledgeBase(
                name=name,
                description=description,
                metadata=json.dumps(metadata) if metadata else None
            )
            db.add(kb)
            db.commit()
            db.refresh(kb)
            return kb

    @staticmethod
    def update(
        kb_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[KnowledgeBase]:
        """Update knowledge base"""
        with Session() as db:
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
            if not kb:
                return None

            if name is not None:
                kb.name = name
            if description is not None:
                kb.description = description
            if metadata is not None:
                kb.metadata = json.dumps(metadata)

            kb.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(kb)
            return kb

    @staticmethod
    def delete(kb_id: str) -> bool:
        """Delete knowledge base"""
        with Session() as db:
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
            if not kb:
                return False

            db.delete(kb)
            db.commit()
            return True
