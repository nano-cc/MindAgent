from typing import Optional
from .base import Tool, ToolType
from app.services.rag_service import RagService


class KnowledgeTool(Tool):
    """Knowledge base retrieval tool"""

    def __init__(self, rag_service: RagService):
        self._rag_service = rag_service
        super().__init(
            name="KnowledgeTool",
            description="从指定知识库中执行相似性检索（RAG）。参数为知识库ID（kbsId）和查询文本（query），返回与查询最相关的知识片段。",
            tool_type=ToolType.FIXED,
            func=self._knowledge_query
        )

    def _knowledge_query(self, kbsId: str, query: str) -> str:
        """Execute knowledge base query"""
        try:
            results = self._rag_service.similarity_search(kbsId, query)
            return "\n".join(results)
        except Exception as e:
            return f"知识库检索失败: {str(e)}"
