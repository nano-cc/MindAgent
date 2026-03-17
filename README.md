# ChatMind Python


## 项目架构

### 核心模块

- **app/models**: SQLAlchemy数据模型定义
- **app/api**: FastAPI路由和接口定义
- **app/services**: 业务逻辑服务层
- **app/agent**: Agent核心实现（基于LangGraph）
- **app/tools**: 工具定义（RAG、文件系统、数据库等）
- **app/utils**: 工具函数和辅助类

### 技术栈

- **Web框架**: FastAPI 0.115.0
- **数据库**: PostgreSQL + SQLAlchemy 2.0.36
- **向量数据库**: ChromaDB 0.6.3
- **LLM框架**: LangChain 0.3.14 + LangGraph 0.2.64
- **支持模型**: OpenAI、Anthropic、DeepSeek、智谱AI

## 功能特性

1. **智能Agent系统**
   - 基于LangGraph的有状态Agent
   - 支持工具调用循环（Think-Execute模式）
   - 实时状态管理和SSE推送
   - 支持最多20步的Agent循环

2. **知识库管理**
   - 文档上传和存储
   - 自动分块和向量化
   - 语义检索（RAG）
   - 使用ChromaDB作为向量存储

3. **工具系统**
   - 知识库检索工具（固定）
   - 文件系统操作工具（可选）
   - 数据库查询工具（可选）
   - 邮件发送工具（可选）
   - 终止和直接回答工具（固定）

4. **聊天会话**
   - 多会话管理
   - 消息持久化
   - SSE实时推送

## API接口文档

所有接口与Java版本完全兼容，响应格式保持一致。

### Agent管理

- `GET /api/agents` - 获取所有Agent
- `POST /api/agents` - 创建Agent
- `DELETE /api/agents/{agentId}` - 删除Agent
- `PATCH /api/agents/{agentId}` - 更新Agent

**创建Agent示例**:
```json
{
  "name": "客服助手",
  "description": "一个智能客服助手",
  "systemPrompt": "你是一个友好的客服助手",
  "model": "gpt-4o",
  "allowedTools": ["KnowledgeTool", "terminate"],
  "allowedKbs": []
}
```

### 会话管理

- `GET /api/chat-sessions` - 获取所有会话
- `GET /api/chat-sessions/{chatSessionId}` - 获取单个会话
- `GET /api/chat-sessions/agent/{agentId}` - 根据AgentID获取会话
- `POST /api/chat-sessions` - 创建会话
- `DELETE /api/chat-sessions/{chatSessionId}` - 删除会话
- `PATCH /api/chat-sessions/{chatSessionId}` - 更新会话

**创建会话示例**:
```json
{
  "agentId": "agent-uuid",
  "title": "新对话"
}
```

### 消息管理

- `GET /api/chat-messages/session/{sessionId}` - 获取会话消息
- `POST /api/chat-messages` - 创建消息（触发Agent处理）
- `DELETE /`/api/chat-messages/{chatMessageId}` - 删除消息
- `PATCH /api/chat-messages/{chatMessageId}` - 更新消息

**创建消息示例（触发Agent）**:
```json
{
  "sessionId": "session-uuid",
  "role": "user",
  "content": "你好，请帮我查询一下用户信息",
  "agentId": "agent-uuid"
}
```

### 知识库管理

- `GET /api/knowledge-bases` - 获取所有知识库
- `POST /api/knowledge-bases` - 创建知识库
- `DELETE /api/knowledge-bases/{knowledgeBaseId}` - 删除知识库
- `PATCH /api/knowledge-bases/{knowledgeBaseId}` - 更新知识库

### 文档管理

- `GET /api/documents` - 获取所有文档
- `GET /api/documents/kb/{kbId}` - 根据知识库ID获取文档
- `POST /api/documents` - 创建文档记录
- `POST /api/documents/upload` - 上传文档文件
- `DELETE /api/documents/{documentId}` - 删除文档
- `PATCH /api/documents/{documentId}` - 更新文档

### 工具管理

- `GET /api/tools` - 获取可用工具列表

### SSE连接

- `GET /sse/connect/{chatSessionId}` - 建立SSE连接接收实时消息

**SSE事件格式**:
```json
{
  "event": "message",
  "data": {
    "type": "ASSISTANT_MESSAGE" | "TOOL_RESULT",
    "message": {
      "role": "assistant" | "tool",
      "content": "消息内容",
      "tool_calls": [...] // 仅ASSISTANT_MESSAGE
    }
  }
}
```

## 快速开始

### 1. 安装依赖

```bash
cd MindAgent
./setup.sh
```

或手动安装：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥和数据库配置
```

**必要配置项**:
- `DATABASE_URL`: PostgreSQL数据库连接字符串
- `OPENAI_API_KEY`: OpenAI API密钥（或使用其他模型）
- `DEEPSEEK_API_KEY`: DeepSeek API密钥（替代方案）
- `ZHIPUAI_API_KEY`: 智谱AI API密钥（替代方案）
- `ANTHROPIC_API_KEY`: Anthropic API密钥（替代方案）

### 3. 初始化数据库

```bash
# 确保PostgreSQL数据库已创建
createdb mindagent

# 激活虚拟环境
source venv/bin/activate

# 运行数据库迁移
alembic upgrade head
```

### 4. 启动服务

```bash
./start.sh
```

或手动启动：
```bash
source venv/bin/activate
python -m app.main
```

服务将在 `http://localhost:8000` 启动。

### 5. 查看API文档

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Agent工作流程

1. **用户创建消息** → 发布到`/api/chat-messages`接口
2. **触发Agent处理** → 如果请求中包含`agentId`
3. **Agent执行Think-Execute循环**：
   - **Think**: LLM决策下一步动作（调用工具或直接回答）
   - **Execute**: 执行工具调用并获取结果
   - 循环直到调用`terminate`工具或达到最大步数（20步）
4. **实时推送** → 所有消息通过SSE实时推送给前端


## 支持的模型

### OpenAI
- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4-turbo`
- `o1-preview`
- `o1-mini-preview`

### Anthropic
- `claude-3-5-sonnet`
- `claude-3-5-haiku`
- `claude-3-opus`
- `claude-3-sonnet`

### DeepSeek
- `deepseek-chat`
- `deepseek-coder`

### 智谱AI
- `glm-4`
- `glm-4-air`
- `glm-4-flash`

## 开发说明

### 添加新工具

1. 在 `app/tools/` 目录创建新工具类
2. 继承 `Tool` 基类或使用LangChain的 `StructuredTool`
3. 在 `ToolService` 中注册工具

**示例**:
```python
from app.tools.base import Tool, ToolType

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="myCustomTool",
            description="自定义工具描述",
            tool_type=ToolType.OPTIONAL,
            func=self._execute
        )

    def _execute(self, param1: str, param2: int) -> str:
        # 执行逻辑
        return "执行结果"
```

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 运行测试

```bash
source venv/bin/activate
pytest tests/
```

## 部署建议

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.main"]
```

### 生产环境配置

1. 使用环境变量管理敏感信息
2. 启用HTTPS（使用Nginx或Traefik）
3. 配置数据库连接池
4. 启用日志记录
5. 配置CORS策略
6. 使用进程管理器（如Supervisor或systemd）

## 故障排查

### 数据库连接失败
- 检查`DATABASE_URL`配置
- 确保PostgreSQL服务正在运行
- 确保数据库已创建

### API密钥错误
- 检查.env文件中的API密钥配置
- 确保API密钥有效且有足够的额度

### 向量数据库错误
- 检查`VECTOR_DB_PATH`目录权限
- 确保ChromaDB版本兼容

### SSE连接断开
- 检查防火墙设置
- 确保WebSocket/SSE连接被允许

## 项目结构

```
chatmind_python/
├── app/
│   ├── agent/          # Agent核心实现
│   │   ├── agent.py
│   │   ├── agent_factory.py
│   │   └── agent_state.py
│   ├── api/            # FastAPI路由
│   │   ├── agents.py
│   │   ├── chat_messages.py
│   │   ├── chat_sessions.py
│   │   ├── documents.py
│   │   ├── knowledge_bases.py
│   │   ├── sse.py
│   │   └── tools.py
│   ├── models/          # SQLAlchemy模型
│   │   ├── agent.py
│   │   ├── chat_message.py
│   │   ├── chat_session.py
│   │   ├── chunk_bge_m3.py
│   │   ├── document.py
│   │   ├── knowledge_base.py
│   │   └── schemas.py
│   ├── services/        # 业务逻辑服务
│   │   ├── agent_service.py
│   │   ├── chat_message_service.py
│   │   ├── chat_session_service.py
│   │   ├── document_service.py
│   │   ├── email_service.py
│   │   ├── knowledge_base_service.py
│   │   ├── markdown_parser_service.py
│   │   ├── rag_service.py
│   │   └── tool_service.py
│   ├── tools/           # 工具定义
│   │   ├── base.py
│   │   ├── database.py
│   │   ├── direct_answer.py
│   │   ├── email.py
│   │   ├── file_system.py
│   │   ├── knowledge.py
│   │   └── terminate.py
│   ├── utils/           # 工具函数
│   │   ├── date_utils.py
│   │   └── id_generator.py
│   ├── config.py        # 配置
│   ├── database.py       # 数据库连接
│   └── main.py          # 应用入口
├── alembic/            # 数据库迁移
├── data/                # 数据目录
├── logs/                # 日志目录
├── requirements.txt      # Python依赖
├── .env.example         # 环境变量示例
├── setup.sh            # 安装脚本
└── start.sh            # 启动脚本
```

## 许可证

MIT License - 详见 LICENSE 文件

## 联系方式

如有问题或建议，请提交Issue或Pull Request。
