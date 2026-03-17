import os
import aiofiles
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import json
import uuid

from app.models import Document
from app.database import Session
from app.config import settings


class DocumentService:
    """Document service for CRUD operations"""

    @staticmethod
    def get_all() -> List[Document]:
        """Get all documents"""
        with Session() as db:
            return db.query(Document).all()

    @staticmethod
    def get_by_kb_id(kb_id: str) -> List[Document]:
        """Get documents by knowledge base ID"""
        with Session() as db:
            return db.query(Document).filter(Document.kb_id == kb_id).all()

    @staticmethod
    def get_by_id(doc_id: str) -> Optional[Document]:
        """Get document by ID"""
        with Session() as db:
            return db.query(Document).filter(Document.id == doc_id).first()

    @staticmethod
    def create(
        kb_id: str,
        filename: str,
        filetype: Optional[str] = None,
        size: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> Document:
        """Create new document record"""
        with Session() as db:
            doc = Document(
                kb_id=kb_id,
                filename=filename,
                filetype=filetype,
                size=size,
                metadata=json.dumps(metadata) if metadata else None
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc

    @staticmethod
    async def upload_document(
        kb_id: str,
        filename: str,
        file_content: bytes,
        filetype: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Document:
        """Upload document and create record"""
        # Ensure storage directory exists
        storage_path = Path(settings.DOCUMENT_STORAGE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        doc_id = str(uuid.uuid4())
        ext = Path(filename).suffix
        stored_filename = f"{doc_id}{ext}"
        file_path = storage_path / stored_filename

        # Write file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        # Create document record
        return DocumentService.create(
            kb_id=kb_id,
            filename=filename,
            filetype=filetype or ext.lstrip('.'),
            size=len(file_content),
            metadata=metadata
        )

    @staticmethod
    def update(
        doc_id: str,
        filename: Optional[str] = None,
        filetype: Optional[str] = None,
        size: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> Optional[Document]:
        """Update document"""
        with Session() as db:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return None

            if filename is not None:
                doc.filename = filename
            if filetype is not None:
                doc.filetype = filetype
            if size is not None:
                doc.size = size
            if metadata is not None:
                doc.metadata = json.dumps(metadata)

            doc.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(doc)
            return doc

    @staticmethod
    def delete(doc_id: str) -> bool:
        """Delete document and its file"""
        with Session() as db:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return False

            # Delete file from storage
            storage_path = Path(settings.DOCUMENT_STORAGE_PATH)
            # Find file with doc_id as prefix
            for file in storage_path.glob(f"{doc_id}*"):
                file.unlink()

            db.delete(doc)
            db.commit()
            return True

    @staticmethod
    def get_file_path(doc_id: str) -> Optional[Path]:
        """Get file path for document"""
        doc = DocumentService.get_by_id(doc_id)
        if not doc:
            return None

        storage_path = Path(settings.DOCUMENT_STORAGE_PATH)
        # Find file with doc_id as prefix
        for file in storage_path.glob(f"{doc_id}*"):
            return file
        return None
