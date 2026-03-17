from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.schemas import (
    CreateAgentRequest,
    UpdateAgentRequest,
    AgentResponse,
    GetAgentsResponse,
    CreateAgentResponse
)
from app.models import Agent as AgentModel
from app.services import AgentService

router = APIRouter(prefix="/api", tags=["agents"])


def _agent_to_response(agent: AgentModel) -> AgentResponse:
    """Convert Agent model to response schema"""
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        model=agent.model,
        allowed_tools=agent.allowed_tools,
        allowed_kbs=agent.allowed_kbs,
        chat_options=agent.chat_options,
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        updated_at=agent.updated_at.isoformat() if agent.updated_at else ""
    )


@router.get("/agents")
async def get_agents() -> GetAgentsResponse:
    """Query all agents"""
    agents = AgentService.get_all_agents()
    return GetAgentsResponse(
        agents=[_agent_to_response(agent) for agent in agents]
    )


@router.post("/agents", response_model=CreateAgentResponse)
async def create_agent(request: CreateAgentRequest) -> CreateAgentResponse:
    """Create agent"""
    try:
        agent = AgentService.create_agent(
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            model=request.model,
            allowed_tools=request.allowed_tools,
            allowed_kbs=request.allowed_kbs,
            chat_options=request.chat_options
        )
        return CreateAgentResponse(agentId=agent.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/agents/{agentId}")
async def delete_agent(agentId: str):
    """Delete agent"""
    try:
        success = AgentService.delete_agent(agentId)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agentId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/agents/{agentId}")
async def update_agent(agentId: str, request: UpdateAgentRequest):
    """Update agent"""
    try:
        agent = AgentService.update_agent(
            agent_id=agentId,
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            model=request.model,
            allowed_tools=request.allowed_tools,
            allowed_kbs=request.allowed_kbs,
            chat_options=request.chat_options
        )
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agentId}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
