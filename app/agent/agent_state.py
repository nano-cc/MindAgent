from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State for agent graph"""
    messages: Annotated[List[BaseMessage], add_messages]
    session_id: str
    agent_id: str
    max_steps: int
    current_step: int
    finished: bool
    last_tool_calls: List[dict]
