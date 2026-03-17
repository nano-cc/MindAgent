from .base import Tool, ToolType


class DirectAnswerTool(Tool):
    """Direct answer tool"""

    def __init__(self):
        super().__init__(
            name="directAnswer",
            description="用于直接回答用户问题，适用于无需生成任务计划或调用其他工具的场景。",
            tool_type=ToolType.FIXED,
            func=self._direct_answer
        )

    def _direct_answer(self, answer: str) -> str:
        """Provide direct answer"""
        return answer
