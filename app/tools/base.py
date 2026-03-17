from enum import Enum
from typing import Callable, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool


class ToolType(str, Enum):
    """Tool type enumeration"""
    FIXED = "FIXED"  # Required tools for all agents
    OPTIONAL = "OPTIONAL"  # Optional tools


class Tool(BaseTool):
    """Base tool class"""
    name: str
    description: str
    tool_type: ToolType

    def __init__(self, name: str, description: str, tool_type: ToolType, func: Callable):
        self.name = name
        self.description = description
        self.tool_type = tool_type
        super().__init__(name=name, description=description, func=func)

    def _run(self, *args, **kwargs):
        return self.func(*args, **kwargs)
