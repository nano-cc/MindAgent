from typing import List
from app.tools import (
    Tool,
    KnowledgeTool,
    TerminateTool,
    DirectAnswerTool,
    FileSystemTool,
    DataBaseTool,
    EmailTool,
    ToolType
)
from app.services.rag_service import RagService


class ToolService:
    """Tool service for managing available tools"""

    def __init__(self, rag_service: RagService):
        self._rag_service = rag_service
        self._tools: List[Tool] = []
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize all tools"""
        # Fixed tools
        self._tools.extend([
            TerminateTool(),
            DirectAnswerTool(),
            KnowledgeTool(self._rag_service),
        ])

        # Optional tools
        self._tools.extend([
            FileSystemTool(),
            DataBaseTool(),
            EmailTool(),
        ])

    def get_all_tools(self) -> List[Tool]:
        """Get all available tools"""
        return self._tools

    def get_fixed_tools(self) -> List[Tool]:
        """Get fixed tools (required for all agents)"""
        return [tool for tool in self._tools if tool.tool_type == ToolType.FIXED]

    def get_optional_tools(self) -> List[Tool]:
        """Get optional tools"""
        return [tool for tool in self._tools if tool.tool_type == ToolType.OPTIONAL]

    def get_tools_by_names(self, tool_names: List[str]) -> List[Tool]:
        """Get tools by names"""
        tool_dict = {tool.name: tool for tool in self._tools}
        return [tool_dict[name] for name in tool_names if name in tool_dict]

    def get_tool_by_name(self, tool_name: str) -> Tool:
        """Get tool by name"""
        for tool in self._tools:
            if tool.name == tool_name:
                return tool
        return None

    def get_tool_list_for_frontend(self) -> List[dict]:
        """Get tool list formatted for frontend"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "type": tool.tool_type.value
            }
            for tool in self._tools
        ]
