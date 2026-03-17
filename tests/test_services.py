import pytest
from app.services import (
    AgentService,
    ChatSessionService,
    KnowledgeBaseService,
    ToolService,
    RagService
)


def test_rag_service():
    """Test RAG service"""
    rag = RagService()
    assert rag.health_check() is True

    # Test embedding
    text = "Test text for embedding"
    embedding = rag.embed(text)
    assert isinstance(embedding, list)
    assert len(embedding) > 0

    # Test similarity search (will return empty for non-existent KB)
    results = rag.similarity_search("test_kb_id", "test query")
    assert isinstance(results, list)


def test_tool_service():
    """Test tool service"""
    rag = RagService()
    tool_service = ToolService(rag)

    # Test get all tools
    all_tools = tool_service.get_all_tools()
    assert len(all_tools) > 0

    # Test get fixed tools
    fixed_tools = tool_service.get_fixed_tools()
    assert len(fixed_tools) > 0

    # Test get optional tools
    optional_tools = tool_service.get_optional_tools()
    assert len(optional_tools) >= 0

    # Test get tool list for frontend
    frontend_tools = tool_service.get_tool_list_for_frontend()
    assert isinstance(frontend_tools, list)


@pytest.mark.asyncio
async def test_agent_service():
    """Test agent service"""
    # Test create agent
    agent = AgentService.create_agent(
        name="Test Agent",
        description="A test agent",
        system_prompt="You are a test assistant",
        model="gpt-4o",
        allowed_tools=["KnowledgeTool", "terminate"],
        allowed_kbs=[],
        chat_options={"temperature": 0.7}
    )
    assert agent.id is not None
    assert agent.name == "Test Agent"

    # Test get agent
    retrieved_agent = AgentService.get_agent_by_id(agent.id)
    assert retrieved_agent is not None
    assert retrieved_agent.id == agent.id

    # Test get all agents
    all_agents = AgentService.get_all_agents()
    assert len(all_agents) >= 1

    # Test update agent
    updated_agent = AgentService.update_agent(
        agent.id,
        description="Updated description"
    )
    assert updated_agent is not None
    assert updated_agent.description == "Updated description"

    # Test delete agent
    success = AgentService.delete_agent(agent.id)
    assert success is True


@pytest.mark.asyncio
async def test_knowledge_base_service():
    """Test knowledge base service"""
    # Test create knowledge base
    kb = KnowledgeBaseService.create(
        name="Test KB",
        description="A test knowledge base",
        metadata={"key": "value"}
    )
    assert kb.id is not None
    assert kb.name == "Test KB"

    # Test get knowledge base
    retrieved_kb = KnowledgeBaseService.get_by_id(kb.id)
    assert retrieved_kb is not None
    assert retrieved_kb.id == kb.id

    # Test get all knowledge bases
    all_kbs = KnowledgeBaseService.get_all()
    assert len(all_kbs) >= 1

    # Test update knowledge base
    updated_kb = KnowledgeBaseService.update(
        kb.id,
        description="Updated description"
    )
    assert updated_kb is not None
    assert updated_kb.description == "Updated description"

    # Test delete knowledge base
    success = KnowledgeBaseService.delete(kb.id)
    assert success is True


@pytest.mark.asyncio
async def test_chat_session_service():
    """Test chat session service"""
    # First create an agent
    agent = AgentService.create_agent(name="Test Agent", model="gpt-4o")

    # Test create session
    session = ChatSessionService.create_session(
        agent_id=agent.id,
        title="Test Session",
        metadata={"test": True}
    )
    assert session.id is not None
    assert session.title == "Test Session"

    # Test get session
    retrieved_session = ChatSessionService.get_session_by_id(session.id)
    assert retrieved_session is not None
    assert retrieved_session.id == session.id

    # Test get sessions by agent ID
    agent_sessions = ChatSessionService.get_sessions_by_agent_id(agent.id)
    assert len(agent_sessions) >= 1

    # Test update session
    updated_session = ChatSessionService.update_session(
        session.id,
        title="Updated Title"
    )
    assert updated_session is not None
    assert updated_session.title == "Updated Title"

    # Cleanup
    ChatSessionService.delete_session(session.id)
    AgentService.delete_agent(agent.id)
