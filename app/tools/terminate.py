from .base import Tool, ToolType


class TerminateTool(Tool):
    """Terminate agent loop tool"""

    def __init__(self):
        super().__init__(
            name="terminate",
            description="如果你觉得当前所有的任务已经执行完毕了，就执行这个工具调用",
            tool_type=ToolType.FIXED,
            func=self._terminate
        )

    def _terminate(self) -> str:
        """Terminate the agent loop"""
        return "任务完成"
