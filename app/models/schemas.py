from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class CreateAgentRequest(BaseModel):
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    model: Optional[str] = Field(None, description="Model name")
    allowed_tools: Optional[List[str]] = Field(None, description="Allowed tool names")
    allowed_kbs: Optional[List[str]] = Field(None, description="Allowed knowledge base IDs")
    chat_options: Optional[Dict[str, Any]] = Field(None, description="Chat options")


class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    allowed_tools: Optional[List[str]] = None
    allowed_kbs: Optional[List[str]] = None
    chat_options: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    allowed_tools: Optional[str] = None  # JSON string
    allowed_kbs: Optional[str] = None  # JSON string
    chat_options: Optional[str] = None  # JSON string
    created_at: str
    updated_at: str


class GetAgentsResponse(BaseModel):
    agents: List[AgentResponse]


class CreateAgentResponse(BaseModel):
    agentId: str


class CreateChatSessionRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID")
    title: Optional[str] = Field(None, description="Session title")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")


class UpdateChatSessionRequest(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatSessionResponse(BaseModel):
    id: str
    agent_id: str
    title: Optional[str] = None
    metadata: Optional[str] = None  # JSON string
    created_at: str
    updated_at: str


class GetChatSessionsResponse(BaseModel):
    chatSessions: List[ChatSessionResponse]


class GetChatSessionResponse(BaseModel):
    id: str
    agent_id: str
    title: Optional[str] = None
    metadata: Optional[str] = None
    created_at: str
    updated_at: str


class CreateChatSessionResponse(BaseModel):
    chatSessionId: str


class CreateChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    role: str = Field(..., description="Message role: user, assistant, tool")
    content: Optional[str] = Field(None, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")
    agent_id: Optional[str] = Field(None, description="Agent ID (for triggering agent)")


class UpdateChatMessageRequest(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: Optional[str] = None
    metadata: Optional[str] = None  # JSON string
    created_at: str
    updated_at: str


class GetChatMessagesResponse(BaseModel):
    chatMessages: List[ChatMessageResponse]


class CreateChatMessageResponse(BaseModel):
    chatMessageId: str


class CreateKnowledgeBaseRequest(BaseModel):
    name: str = Field(..., description="Knowledge base name")
    description: Optional[str] = Field(None, description="Knowledge base description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Knowledge base metadata")


class UpdateKnowledgeBaseRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    metadata: Optional[str] = None  # JSON string
    created_at: str
    updated_at: str


class GetKnowledgeBasesResponse(BaseModel):
    knowledgeBases: List[KnowledgeBaseResponse]


class CreateKnowledgeBaseResponse(BaseModel):
    knowledgeBaseId: str


class CreateDocumentRequest(BaseModel):
    kb_id: str = Field(..., description="Knowledge base ID")
    filename: str = Field(..., description="Document filename")
    filetype: Optional[str] = Field(None, description="File type")
    size: Optional[int] = Field(None, description="File size in bytes")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")


class UpdateDocumentRequest(BaseModel):
    filename: Optional[str] = None
    filetype: Optional[str] = None
    size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: str
    kb_id: str
    filename: str
    filetype: Optional[str] = None
    size: Optional[int] = None
    metadata: Optional[str] = None  # JSON string
    created_at: str
    updated_at: str


class GetDocumentsResponse(BaseModel):
    documents: List[DocumentResponse]


class CreateDocumentResponse(BaseModel):
    documentId: str


class ToolResponse(BaseModel):
    name: str
    description: str
    type: str
