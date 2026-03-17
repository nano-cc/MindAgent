from typing import List, Optional
from datetime import datetime
import json

from app.models import ChatSession
from app.database import Session


class ChatSessionService:
    """Chat session service for CRUD operations"""

    @staticmethod
    def get_all_sessions() -> List[ChatSession]:
        """Get all chat sessions"""
        with Session() as db:
            return db.query(ChatSession).all()

    @staticmethod
    def get_session_by_id(session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        with Session() as db:
            return db.query(ChatSession).filter(ChatSession.id == session_id).first()

    @staticmethod
    def get_sessions_by_agent_id(agent_id: str) -> List[ChatSession]:
        """Get sessions by agent ID"""
        with Session() as db:
            return db.query(ChatSession).filter(ChatSession.agent_id == agent_id).all()

    @staticmethod
    def create_session(
        agent_id: str,
        title: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> ChatSession:
        """Create new chat session"""
        with Session() as db:
            session = ChatSession(
                agent_id=agent_id,
                title=title,
                metadata=json.dumps(metadata) if metadata else None
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session

    @staticmethod
    def update_session(
        session_id: str,
        title: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[ChatSession]:
        """Update chat session"""
        with Session() as db:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                return None

            if title is not None:
                session.title = title
            if metadata is not None:
                session.metadata = json.dumps(metadata)

            session.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
            return session

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete chat session"""
        with Session() as db:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                return False

            db.delete(session)
            db.commit()
            return True
