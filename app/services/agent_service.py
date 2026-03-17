from typing import List, Optional
from datetime import datetime
import json

from app.models import Agent
from app.database import Session


class AgentService:
    """Agent service for CRUD operations"""

    @staticmethod
    def get_all_agents() -> List[Agent]:
        """Get all agents"""
        with Session() as db:
            return db.query(Agent).all()

    @staticmethod
    def get_agent_by_id(agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        with Session() as db:
            return db.query(Agent).filter(Agent.id == agent_id).first()

    @staticmethod
    def create_agent(
        name: str,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        allowed_kbs: Optional[List[str]] = None,
        chat_options: Optional[dict] = None
    ) -> Agent:
        """Create new agent"""
        with Session() as db:
            agent = Agent(
                name=name,
                description=description,
                system_prompt=system_prompt,
                model=model,
                allowed_tools=json.dumps(allowed_tools) if allowed_tools else None,
                allowed_kbs=json.dumps(allowed_kbs) if allowed_kbs else None,
                chat_options=json.dumps(chat_options) if chat_options else None
            )
            db.add(agent)
            db.commit()
            db.refresh(agent)
            return agent

    @staticmethod
    def update_agent(
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        allowed_kbs: Optional[List[str]] = None,
        chat_options: Optional[dict] = None
    ) -> Optional[Agent]:
        """Update agent"""
        with Session() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                return None

            if name is not None:
                agent.name = name
            if description is not None:
                agent.description = description
            if system_prompt is not None:
                agent.system_prompt = system_prompt
            if model is not None:
                agent.model = model
            if allowed_tools is not None:
                agent.allowed_tools = json.dumps(allowed_tools)
            if allowed_kbs is not None:
                agent.allowed_kbs = json.dumps(allowed_kbs)
            if chat_options is not None:
                agent.chat_options = json.dumps(chat_options)

            agent.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(agent)
            return agent

    @staticmethod
    def delete_agent(agent_id: str) -> bool:
        """Delete agent"""
        with Session() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                return False

            db.delete(agent)
            db.commit()
            return True
