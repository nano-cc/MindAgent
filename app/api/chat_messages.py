from fastapi import APIRouter, HTTPException, status
import asyncio

from app.models.schemas import (
    CreateChatMessageRequest,
    UpdateChatMessageRequest,
    ChatMessageResponse,
    GetChatMessagesResponse,
    CreateChatMessageResponse
)
from app.models import ChatMessage as ChatMessageModel
from app.services import ChatMessageService
from app.api.sse import send_sse_message

router = APIRouter(prefix="/api", tags=["chat-messages"])

# Global reference to agent factory (will be set in main.py)
agent_factory = None


def _message_to_response(message: ChatMessageModel) -> ChatMessageResponse:
    """Convert ChatMessage model to response schema"""
    return ChatMessageResponse(
        id=message.id,
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        metadata=message.metadata,
        created_at=message.created_at.isoformat() if message.created_at else "",
        updated_at=message.updated_at.isoformat() if message.updated_at else ""
    )


@router.get("/chat-messages/session/{sessionId}")
async def get_chat_messages_by_session_id(sessionId: str) -> GetChatMessagesResponse:
    """Query chat messages by session ID"""
    messages = ChatMessageService.get_messages_by_session_id(sessionId)
    return GetChatMessagesResponse(
        chatMessages=[_message_to_response(msg) for msg in messages]
    )


@router.post("/chat-messages", response_model=CreateChatMessageResponse)
async def create_chat_message(request: CreateChatMessageRequest) -> CreateChatMessageResponse:
    """Create chat message (triggers agent processing if agent_id is provided)"""
    try:
        # Create message in database
        message = ChatMessageService.create_message(
            session_id=request.session_id,
            role=request.role,
            content=request.content,
            metadata=request.metadata
        )

        # Send SSE notification for user message
        send_sse_message(request.session_id, {
            "type": "USER_MESSAGE",
            "message": {
                "id": message.id,
                "role": request.role,
                "content": request.content
            }
        })

        # If agent_id is provided, trigger agent processing asynchronously
        if request.agent_id and agent_factory:
            # Run agent in background
            asyncio.create_task(_run_agent_background(
                request.agent_id,
                request.session_id
            ))

        return CreateChatMessageResponse(chatMessageId=message.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def _run_agent_background(agent_id: str, session_id: str):
    """Run agent in background task"""
    try:
        # Create SSE callback
        def sse_callback(msg: dict):
            send_sse_message(session_id, msg)

        # Create agent instance
        agent = agent_factory.create(
            agent_id=agent_id,
            session_id=session_id,
            sse_callback=sse_callback
        )
        # Run agent
        agent.run()
    except Exception as e:
        print(f"Error running agent: {e}")
        # Send error message via SSE
        send_sse_message(session_id, {
            "type": "ERROR",
            "message": {
                "error": str(e)
            }
        })


@router.delete("/chat-messages/{chatMessageId}")
async def delete_chat_message(chatMessageId: str):
    """Delete chat message"""
    try:
        success = ChatMessageService.delete_message(chatMessageId)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message not found: {chatMessageId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/chat-messages/{chatMessageId}")
async def update_chat_message(chatMessageId: str, request: UpdateChatMessageRequest):
    """Update chat message"""
    try:
        message = ChatMessageService.update_message(
            message_id=chatMessageId,
            content=request.content,
            metadata=request.metadata
        )
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message not found: {chatMessageId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
