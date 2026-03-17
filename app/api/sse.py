import asyncio
import json
from typing import Dict, Set
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/sse", tags=["sse"])

# Store SSE connections
sse_connections: Dict[str, Set[asyncio.Queue]] = {}


async def sse_event_generator(session_id: str):
    """Generate SSE events for a session"""
    queue: asyncio.Queue = asyncio.Queue()
    if session_id not in sse_connections:
        sse_connections[session_id] = set()
    sse_connections[session_id].add(queue)

    try:
        while True:
            data = await queue.get()
            yield {
                "event": "message",
                "data": json.dumps(data)
            }
    except asyncio.CancelledError:
        pass
    finally:
        # Clean up connection
        if session_id in sse_connections:
            sse_connections[session_id].discard(queue)
            if not sse_connections[session_id]:
                del sse_connections[session_id]


def send_sse_message(session_id: str, message: dict):
    """Send SSE message to all connections for a session"""
    if session_id in sse_connections:
        for queue in sse_connections[session_id]:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass


@router.get("/connect/{chatSessionId}")
async def sse_connect(chatSessionId: str):
    """Handle SSE connection"""
    return EventSourceResponse(
        content=sse_event_generator(chatSessionId),
        media_type="text/event-stream"
    )
