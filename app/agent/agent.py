from typing import List, Optional, Callable
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)
from langchain_core.runnser import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import StructuredTool

from app.agent.agent_state import AgentState
from app.agent.agent_status import AgentStatus
from app.services import (
    ChatMessageService,
    ChatSessionService,
    AgentService
)
from app.models import Agent as AgentModel, ChatSession
from app.config import settings


class MindAgent:
    """JChatMind Agent using LangGraph"""

    def __init__(
        self,
        agent_id: str,
        session_id: str,
        agent: AgentModel,
        session: ChatSession,
        available_tools: List,
        available_kbs: List[dict],
        llm: any,
        sse_callback: Optional[Callable] = None
    ):
        self.agent_id = agent_id
        self.session_id = session_id
        self.agent = agent
        self.session = session
        self.available_tools = available_tools
        self.available_kbs = available_kbs
        self.llm = llm
        self.sse_callback = sse_callback

        self.status = AgentStatus.IDLE
        self.max_steps = settings.MAX_AGENT_STEPS or 20
        self.max_messages = settings.MAX_CHAT_MESSAGES or 20

        # Load chat history
        self.messages = self._load_chat_history()

        # Build agent graph
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()

    def _load_chat_history(self) -> List:
        """Load chat history from database"""
        messages = []
        recent_msgs = ChatMessageService.get_recent_messages_by_session_id(
            self.session_id,
            self.max_messages
        )

        # Convert to LangChain messages
        for msg in reversed(recent_msgs):
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
            elif msg.role == "tool":
                messages.append(ToolMessage(content=msg.content))

        # Add system prompt
        if self.agent.system_prompt:
            messages.insert(0, SystemMessage(content=self.agent.system_prompt))

        return messages

    def _build_graph(self):
        """Build LangGraph for agent"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("think", self._think_node)
        workflow.add_node("execute", self._execute_node)

        # Add edges
        workflow.set_entry_point("think")
        workflow.add_conditional_edges(
            "think",
            self._should_execute,
            {
                "execute": "execute",
                "end": END
            }
        )
        workflow.add_conditional_edges(
            "execute",
            self._should_continue,
            {
                "continue": "think",
                "end": END
            }
        )

        return workflow.compile(checkpointer=self.checkpointer)

    def _should_execute(self, state: AgentState) -> str:
        """Determine if we should execute tools or end"""
        # Check if we've reached max steps
        if state["current_step"] >= state["max_steps"]:
            return "end"

        # Check if there are tool calls in last message
        if state["last_tool_calls"]:
            return "execute"

        # Check if last tool was terminate
        if state["last_tool_calls"]:
            for tool_call in state["last_tool_calls"]:
                if tool_call.get("name") == "terminate":
                    return "end"

        return "end"

    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue or end"""
        # Check if we've reached max steps
        if state["current_step"] >= state["max_steps"]:
            return "end"

        return "continue"

    def _think_node(self, state: AgentState) -> AgentState:
        """Think node: LLM decides next action"""
        self.status = AgentStatus.THINKING

        # Build context with available knowledge bases
        kb_info = "\n".join([
            f"- {kb.get('name')}: {kb.get('description', '')}"
            for kb in self.available_kbs
        ])

        system_instruction = f"""
现在你是一个智能的具体「决策模块」
请根据当前对话上下文，决定下一步的动作。

【额外信息】
- 你目前拥有的知识库列表以及描述：
{kb_info}
- 如果有缺失的上下文时，优先从知识库中进行搜索

【可用工具】
{', '.join([tool.name if hasattr(tool, 'name') else str(tool) for tool in self.available_tools])}

请根据用户的问题和对话历史，决定：
1. 是否需要调用工具
2. 如果需要，选择哪个工具
3. 如果不需要，直接回答用户的问题
"""

        # Prepare messages with system instruction
        messages_for_llm = [
            SystemMessage(content=system_instruction)
        ] + state["messages"]

        # Invoke LLM
        response = self.llm.invoke(messages_for_llm)

        # Extract tool calls
        tool_calls = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_calls = [
                {
                    "name": tc.name,
                    "args": tc.args,
                    "id": tc.id
                }
                for tc in response.tool_calls
            ]

        # Update state
        state["messages"].append(response)
        state["last_tool_calls"] = tool_calls

        # Save message to database
        self._save_message("assistant", response.content,
                           metadata={"tool_calls": tool_calls})

        # Send SSE notification
        if self.sse_callback:
            self.sse_callback({
                "type": "ASSISTANT_MESSAGE",
                "message": {
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": tool_calls
                }
            })

        return state

    def _execute_node(self, state: AgentState) -> AgentState:
        """Execute node: Execute tool calls"""
        self.status = AgentStatus.EXECUTING

        tool_calls = state["last_tool_calls"]
        tool_results = []

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Find and execute tool
            tool = None
            for t in self.available_tools:
                if hasattr(t, 'name') and t.name == tool_name:
                    tool = t
                    break

            if not tool:
                result = f"错误：工具 '{tool_name}' 不存在"
            else:
                try:
                    # Execute tool with args
                    result = tool.invoke(tool_args) if hasattr(
                        tool, 'invoke') else tool(**tool_args)
                except Exception as e:
                    result = f"工具执行错误: {str(e)}"

            tool_results.append({
                "name": tool_name,
                "result": result
            })

            # Save tool result to database
            self._save_message("tool", result, metadata={
                "tool_name": tool_name,
                "tool_args": tool_args
            })

            # Send SSE notification
            if self.sse_callback:
                self.sse_callback({
                    "type": "TOOL_RESULT",
                    "message": {
                        "role": "tool",
                        "content": result,
                        "tool_name": tool_name
                    }
                })

        # Add tool result messages to state
        for tool_result in tool_results:
            state["messages"].append(
                ToolMessage(
                    content=tool_result["result"],
                    tool_call_id=tool_result["args"].get(
                        "id", "") if "args" in tool_result else ""
                )
            )

        # Clear last tool calls and increment step
        state["last_tool_calls"] = []
        state["current_step"] += 1

        return state

    def _save_message(self, role: str, content: str, metadata: dict = None):
        """Save message to database"""
        try:
            ChatMessageService.create_message(
                session_id=self.session_id,
                role=role,
                content=content,
                metadata=metadata
            )
        except Exception as e:
            print(f"Error saving message: {e}")

    def run(self):
        """Run the agent"""
        if self.status != AgentStatus.IDLE:
            raise ValueError("Agent is not idle")

        try:
            self.status = AgentStatus.THINKING

            # Initial state
            initial_state = {
                "messages": self.messages,
                "session_id": self.session_id,
                "agent_id": self.agent_id,
                "max_steps": self.max_steps,
                "current_step": 0,
                "finished": False,
                "last_tool_calls": []
            }

            # Run graph
            config = RunnableConfig(
                configurable={"thread_id": self.session_id}
            )

            final_state = self.graph.invoke(initial_state, config)

            self.status = AgentStatus.FINISHED
            return final_state

        except Exception as e:
            self.status = AgentStatus.ERROR
            print(f"Agent error: {e}")
            raise
