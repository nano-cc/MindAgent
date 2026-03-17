from fastapi import APIRouter

from app.models.schemas import ToolResponse
from app.services import ToolService

router = APIRouter(prefix="/api", tags=["tools"])

# Global reference to tool service (will be set in main.py)
tool_service = None


@router.get("/tools")
async def get_optional_tools():
    """Get optional tools for frontend"""
    if tool_service:
        tools = tool_service.get_tool_list_for_frontend()
        return {
            "tools": tools
        }
    return {"tools": []}
