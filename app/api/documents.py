from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pathlib import Path

from app.models.schemas import (
    CreateDocumentRequest,
    UpdateDocumentRequest,
    DocumentResponse,
    GetDocumentsResponse,
    CreateDocumentResponse
)
from app.models import Document as DocumentModel
from app.services import DocumentService

router = APIRouter(prefix="/api", tags=["documents"])


def _doc_to_response(doc: DocumentModel) -> DocumentResponse:
    """Convert Document model to response schema"""
    return DocumentResponse(
        id=doc.id,
        kb_id=doc.kb_id,
        filename=doc.filename,
        filetype=doc.filetype,
        size=doc.size,
        metadata=doc.metadata,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else ""
    )


@router.get("/documents")
async def get_documents() -> GetDocumentsResponse:
    """Query all documents"""
    docs = DocumentService.get_all()
    return GetDocumentsResponse(
        documents=[_doc_to_response(doc) for doc in docs]
    )


@router.get("/documents/kb/{kbId}")
async def get_documents_by_kb_id(kbId: str) -> GetDocumentsResponse:
    """Query documents by knowledge base ID"""
    docs = DocumentService.get_by_kb_id(kbId)
    return GetDocumentsResponse(
        documents=[_doc_to_response(doc) for doc in docs]
    )


@router.post("/documents", response_model=CreateDocumentResponse)
async def create_document(request: CreateDocumentRequest) -> CreateDocumentResponse:
    """Create document record (without file upload)"""
    try:
        doc = DocumentService.create(
            kb_id=request.kb_id,
            filename=request.filename,
            filetype=request.filetype,
            size=request.size,
            metadata=request.metadata
        )
        return CreateDocumentResponse(documentId=doc.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/documents/upload", response_model=CreateDocumentResponse)
async def upload_document(
    kbId: str,
    file: UploadFile = File(...)
) -> CreateDocumentResponse:
    """Upload document file"""
    try:
        # Read file content
        content = await file.read()

        # Determine file type
        filetype = file.content_type
        if not filetype:
            ext = Path(file.filename).suffix.lstrip('.')
            filetype = ext or "unknown"

        # Upload document
        doc = await DocumentService.upload_document(
            kb_id=kbId,
            filename=file.filename,
            file_content=content,
            filetype=filetype
        )
        return CreateDocumentResponse(documentId=doc.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/documents/{documentId}")
async def delete_document(documentId: str):
    """Delete document"""
    try:
        success = DocumentService.delete(documentId)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {documentId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/documents/{documentId}")
async def update_document(documentId: str, request: UpdateDocumentRequest):
    """Update document"""
    try:
        doc = DocumentService.update(
            doc_id=documentId,
            filename=request.filename,
            filetype=request.filetype,
            size=request.size,
            metadata=request.metadata
        )
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {documentId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
