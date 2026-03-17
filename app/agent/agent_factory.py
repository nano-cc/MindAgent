from typing import List, Optional, Callable
import json

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from app.agent.agent import MindAgent
from app.services import (
    AgentService,
    ChatSessionService,
    KnowledgeBaseService,
    ToolService
)
from app.models import Agent as AgentModel, ChatSession
from app.config import settings


class AgentFactory:
    """Factory for creating JChatMind agent instances"""

    def __init__(self, tool_service: ToolService):
        self.tool_service = tool_service

    def create(
        self,
        agent_id: str,
        session_id: str,
        sse_callback: Optional[Callable] = None
    ) -> MindAgent:
        """Create a JChatMind agent instance"""
        # Load agent configuration
        agent = AgentService.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        # Load session
        session = ChatSessionService.get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Get available tools
        allowed_tools = []
        if agent.allowed_tools:
            try:
                allowed_tool_names = json.loads(agent.allowed_tools)
                allowed_tools = self.tool_service.get_tools_by_names(
                    allowed_tool_names)
            except json.JSONDecodeError:
                pass
        else:
            # Use fixed tools by default
            allowed_tools = self.tool_service.get_fixed_tools()

        # Get available knowledge bases
        allowed_kbs = []
        if agent.allowed_kbs:
            try:
                allowed_kb_ids = json.loads(agent.allowed_kbs)
                allowed_kbs = []
                for kb_id in allowed_kb_ids:
                    kb = KnowledgeBaseService.get_by_id(kb_id)
                    if kb:
                        allowed_kbs.append({
                            "id": kb.id,
                            "name": kb.name,
                            "description": kb.description
                        })
            except json.JSONDecodeError:
                pass

        # Create LLM instance
        llm = self._create_llm(agent.model)

        # Create agent
        return MindAgent(
            agent_id=agent_id,
            session_id=session_id,
            agent=agent,
            session=session,
            available_tools=allowed_tools,
            available_kbs=allowed_kbs,
            llm=llm,
            sse_callback=sse_callback
        )

    def _create_llm(self, model: Optional[str]):
        """Create LLM instance based on model name"""
        model = model or "gpt-4o"

        if model.startswith("gpt-") or model.startswith("o1-"):
            # OpenAI model
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")

            return ChatOpenAI(
                model=model,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.7
            )

        elif model.startswith("claude-"):
            # Anthropic model
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not configured")

            return ChatAnthropic(
                model=model,
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.7
            )

        elif model.startswith("deepseek-"):
            # DeepSeek model (using OpenAI-compatible API)
            if not settings.DEEPSEEK_API_KEY:
                raise ValueError("DeepSeek API key not configured")

            return ChatOpenAI(
                model=model,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com/v1",
                temperature=0.7
            )

        elif model.startswith("glm-"):
            # Zhipu AI model (using OpenAI-compatible API)
            if not settings.ZHIPUAI_API_KEY:
                raise ValueError("Zhipu AI API key not configured")

            return ChatOpenAI(
                model=model,
                api_key=settings.ZHIPUAI_API_KEY,
                base_url="https://open.big.bigmodel.cn/api/paas/v4/",
                model_kwargs={"encoding_format": "json"}
            )

        else:
            # Default to gpt-4o
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")

            return ChatOpenAI(
                model="gpt-4o",
                api_key=settings.OPENAI_API_KEY,
                temperature=0.7
            )
