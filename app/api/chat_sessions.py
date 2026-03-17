from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    CreateChatSessionRequest,
    UpdateChatSessionRequest,
    ChatSessionResponse,
    GetChatSessionsResponse,
    GetChatSessionResponse,
    CreateChatSessionResponse
)
from app.models import ChatSession as ChatSessionModel
from app.services import ChatSessionService

router = APIRouter(prefix="/api", tags=["chat-sessions"])


def _session_to_response(session: ChatSessionModel) -> ChatSessionResponse:
    """Convert ChatSession model to response schema"""
    return ChatSessionResponse(
        id=session.id,
        agent_id=session.agent_id,
        title=session.title,
        metadata=session.metadata,
        created_at=session.created_at.isoformat() if session.created_at else "",
        updated_at=session.updated_at.isoformat() if session.updated_at else ""
    )


@router.get("/chat-sessions")
async def get_chat_sessions() -> GetChatSessionsResponse:
    """Query all chat sessions"""
    sessions = ChatSessionService.get_all_sessions()
    return GetChatSessionsResponse(
        chatSessions=[_session_to_response(session) for session in sessions]
    )


@router.get("/chat-sessions/{chatSessionId}")
async def get_chat_session(chatSessionId: str) -> GetChatSessionResponse:
    """Query single chat session"""
    session = ChatSessionService.get_session_by_id(chatSessionId)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {chatSessionId}"
        )
    return GetChatSessionResponse(
        id=session.id,
        agent_id=session.agent_id,
        title=session.title,
        metadata=session.metadata,
        created_at=session.created_at.isoformat() if session.created_at else "",
        updated_at=session.updated_at.isoformat() if session.updated_at else ""
    )


@router.get("/chat-sessions/agent/{agentId}")
async def get_chat_sessions_by_agent_id(agentId: str) -> GetChatSessionsResponse:
    """Query chat sessions by agent ID"""
    sessions = ChatSessionService.get_sessions_by_agent_id(agentId)
    return GetChatSessionsResponse(
        chatSessions=[_session_to_response(session) for session in sessions]
    )


@router.post("/chat-sessions", response_model=CreateChatSessionResponse)
async def create_chat_session(request: CreateChatSessionRequest) -> CreateChatSessionResponse:
    """Create chat session"""
    try:
        session = ChatSessionService.create_session(
            agent_id=request.agent_id,
            title=request.title,
            metadata=request.metadata
        )
        return CreateChatSessionResponse(chatSessionId=session.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/chat-sessions/{chatSessionId}")
async def delete_chat_session(chatSessionId: str):
    """Delete chat session"""
    try:
        success = ChatSessionService.delete_session(chatSessionId)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {chatSessionId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/chat-sessions/{chatSessionId}")
async def update_chat_session(chatSessionId: str, request: UpdateChatSessionRequest):
    """Update chat session"""
    try:
        session = ChatSessionService.update_session(
            session_id=chatSessionId,
            title=request.title,
            metadata=request.metadata
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {chatSessionId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
