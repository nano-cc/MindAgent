from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    CreateKnowledgeBaseRequest,
    UpdateKnowledgeBaseRequest,
    KnowledgeBaseResponse,
    GetKnowledgeBasesResponse,
    CreateKnowledgeBaseResponse
)
from app.models import KnowledgeBase as KnowledgeBaseModel
from app.services import KnowledgeBaseService

router = APIRouter(prefix="/api", tags=["knowledge-bases"])


def _kb_to_response(kb: KnowledgeBaseModel) -> KnowledgeBaseResponse:
    """Convert KnowledgeBase model to response schema"""
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        metadata=kb.metadata,
        created_at=kb.created_at.isoformat() if kb.created_at else "",
        updated_at=kb.updated_at.isoformat() if kb.updated_at else ""
    )


@router.get("/knowledge-bases")
async def get_knowledge_bases() -> GetKnowledgeBasesResponse:
    """Query all knowledge bases"""
    kbs = KnowledgeBaseService.get_all()
    return GetKnowledgeBasesResponse(
        knowledgeBases=[_kb_to_response(kb) for kb in kbs]
    )


@router.post("/knowledge-bases", response_model=CreateKnowledgeBaseResponse)
async def create_knowledge_base(request: CreateKnowledgeBaseRequest) -> CreateKnowledgeBaseResponse:
    """Create knowledge base"""
    try:
        kb = KnowledgeBaseService.create(
            name=request.name,
            description=request.description,
            metadata=request.metadata
        )
        return CreateKnowledgeBaseResponse(knowledgeBaseId=kb.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/knowledge-bases/{knowledgeBaseId}")
async def delete_knowledge_base(knowledgeBaseId: str):
    """Delete knowledge base"""
    try:
        success = KnowledgeBaseService.delete(knowledgeBaseId)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge base not found: {knowledgeBaseId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/knowledge-bases/{knowledgeBaseId}")
async def update_knowledge_base(knowledgeBaseId: str, request: UpdateKnowledgeBaseRequest):
    """Update knowledge base"""
    try:
        kb = KnowledgeBaseService.update(
            kb_id=knowledgeBaseId,
            name=request.name,
            description=request.description,
            metadata=request.metadata
        )
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge base not found: {knowledgeBaseId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
