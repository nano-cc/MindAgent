from typing import List, Optional
from datetime import datetime
import json

from app.models import ChatMessage
from app.database import Session


class ChatMessageService:
    """Chat message service for CRUD operations"""

    @staticmethod
    def get_messages_by_session_id(session_id: str) -> List[ChatMessage]:
        """Get messages by session ID"""
        with Session() as db:
            return db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).all()

    @staticmethod
    def get_recent_messages_by_session_id(session_id: str, limit: int = 20) -> List[ChatMessage]:
        """Get recent messages by session ID"""
        with Session() as db:
            return db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    @staticmethod
    def create_message(
        session_id: str,
        role: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> ChatMessage:
        """Create new message"""
        with Session() as db:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                metadata=json.dumps(metadata) if metadata else None
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message

    @staticmethod
    def update_message(
        message_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[ChatMessage]:
        """Update message"""
        with Session() as db:
            message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if not message:
                return None

            if content is not None:
                message.content = content
            if metadata is not None:
                message.metadata = json.dumps(metadata)

            message.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(message)
            return message

    @staticmethod
    def append_message(message_id: str, content: str) -> Optional[ChatMessage]:
        """Append content to message"""
        with Session() as db:
            message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if not message:
                return None

            current_content = message.content or ""
            message.content = current_content + content
            message.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(message)
            return message

    @staticmethod
    def delete_message(message_id: str) -> bool:
        """Delete message"""
        with Session() as db:
            message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if not message:
                return False

            db.delete(message)
            db.commit()
            return True
