import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, engine
from app.api import (
    agents_router,
    chat_sessions_router,
    chat_messages_router,
    knowledge_bases_router,
    documents_router,
    tools_router,
    sse_router
)
from app.services import ToolService, RagService
from app.agent import AgentFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting ChatMind Python...")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"App Host: {settings.APP_HOST}:{settings.APP_PORT}")

    # Initialize database
    print("Initializing database...")
    init_db()

    # Initialize services
    print("Initializing services...")
    rag_service = RagService()
    tool_service = ToolService(rag_service)

    # Create agent factory
    agent_factory = AgentFactory(tool_service)

    # Set global references
    from app.api import chat_messages
    chat_messages.agent_factory = agent_factory

    from app.api import tools
    tools.tool_service = tool_service

    # Store services in app state
    app.state.rag_service = rag_service
    app.state.tool_service = tool_service
    app.state.agent_factory = agent_factory

    print("Services initialized successfully")
    print("ChatMind Python is ready!")

    yield

    # Shutdown
    print("Shutting down...")
    engine.dispose()
    print("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="ChatMind Python - LangChain + LangGraph implementation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(
        ",") if settings.CORS_ORIGINS and settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents_router)
app.include_router(chat_sessions_router)
app.include_router(chat_messages_router)
app.include_router(knowledge_bases_router)
app.include_router(documents_router)
app.include_router(tools_router)
app.include_router(sse_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "database": "ok",
            "vector_store": "ok" if app.state.rag_service.health_check() else "error"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level="info" if not settings.APP_DEBUG else "debug"
    )
