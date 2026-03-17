# ChatMind Python - 项目架构文档

## 项目概述

ChatMind Python 是使用 LangChain + LangGraph 复刻 Java 版本 ChatMind 项目的高可用 Python 实现。提供与 Java 版本完全兼容的 API 接口，可以无缝替换后端服务。

## 技术架构对比

### Java 版本

```
Spring Boot Application
├── Controller Layer (REST API)
├── Service Layer (Business Logic)
├── Agent System (Spring AI)
│   ├── Think Node
│   ├── Execute Node
│   └── Tool Calling Manager
├── Tools (Spring AI Tool Callback)
├── RAG Service (Vector Search)
├── Event System (Spring Events)
└── Persistence (MyBatis + PostgreSQL)
```

**核心技术栈**：
- Spring Boot 3.5.8
- Spring AI 1.1.0
- MyBatis 3.0.3
- PostgreSQL
- DeepSeek/智谱AI 集成

### Python 版本

```
FastAPI Application
├── API Layer (FastAPI Routers)
├── Service Layer (Business Logic)
├── Agent System (LangGraph)
│   ├── Think Node
│   ├── Execute Node
│   └── State Management
├── Tools (LangChain Structured Tools)
├── RAG Service (ChromaDB + LangChain)
├── SSE Real-time Push
└── Persistence (SQLAlchemy + PostgreSQL)
```

**核心技术栈**：
- FastAPI 0.115.0
- LangChain 0.3.14
- LangGraph 0.2.64
- SQLAlchemy 2.0.36
- PostgreSQL
- ChromaDB 0.6.3
- OpenAI/Anthropic/DeepSeek/智谱AI 集成

## 模块设计

### 1. 数据模型层 (app/models/)

**职责**：定义数据库表结构和API响应模式

**主要模型**：
```
Agent          - 智能体配置
ChatSession     - 聊天会话
ChatMessage     - 聊天消息
KnowledgeBase  - 知识库
Document        -   文档
ChunkBgeM3     - 向量分块（BGE-M3嵌入）
```

**数据库映射**：
- 使用 SQLAlchemy ORM
- 自动管理 created_at 和 updated_at
- JSON字段存储复杂数据（allowed_tools、allowed_kbs、metadata等）

### 2. API接口层 (app/api/)

**职责**：定义REST API端点，处理HTTP请求

**路由模块**：
```
agents.py         - /api/agents
chat_sessions.py  - /api/chat-sessions
chat_messages.py  - /api/chat-messages
knowledge_bases.py - /api/knowledge-bases
documents.py     - /api/documents
tools.py        - /api/tools
sse.py         - /sse/connect/{chatSessionId}
```

**兼容性保证**：
- 请求/响应格式与Java版本完全一致
- 使用相同的路径和HTTP方法
- 保持字段命名规范一致

### 3. 服务层 (app/services/)

**职责**：实现业务逻辑，连接数据访问和业务规则

**核心服务**：

#### AgentService
- CRUD操作
- Agent配置管理
- 工具和知识库权限验证

#### ChatSessionService
- 会话生命周期管理
- 按Agent查询会话

#### ChatMessageService
- 消息持久化
- 最近消息查询（用于上下文）

#### KnowledgeBaseService
- 知识库CRUD
- 关联文档管理

#### DocumentService
- 文件存储管理
- 元数据维护

#### ToolService
- 工具注册和发现
- 按类型分组工具（FIXED/OPTIONAL）
- 前端工具列表生成

#### RagService
- 向量数据库操作（ChromaDB）
- 嵌入生成
- 相似性搜索

#### EmailService
- 异步邮件发送
- 配置管理

#### MarkdownParserService
- Markdown解析和渲染
- 文档分块

### 4. Agent系统 (app/agent/)

**职责**：实现智能体核心逻辑，使用LangGraph构建有状态图

**核心组件**：

#### AgentState
- LangGraph状态定义
- 消息历史管理
- 工具调用追踪
- 步数控制

#### AgentStatus
- IDLE - 空闲
- PLANNING - 计划中
- THINKING - 思考中
- EXECUTING - 执行中
- FINISHED - 正常结束
- ERROR - 错误结束

#### JChatMind（Agent实现）
- Think节点：LLM决策下一步动作
- Execute节点：执行工具调用
- 循环控制：最多20步或调用terminate

#### JChatMindFactory
- Agent实例工厂
- LLM选择（根据model配置）
- 工具和知识库加载
- SSE回调配置

**LangGraph工作流**：
```
[Think] --有工具调用?--> [Execute] --未完成?--> [Think]
   |                          |
   +--无工具调用/完成-------+
```

### 5. 工具系统 (app/tools/)

**职责**：定义可被Agent调用的工具

**工具类型**：

#### FIXED工具（所有Agent必需）
1. **KnowledgeTool**
   - 知识库语义检索
   - 使用RAG Service
   - 参数：kbsId, query

2. **TerminateTool**
   - 终止Agent循环
   - 无参数

3. **DirectAnswerTool**
   - 直接回答用户问题
   - 参数：answer

#### OPTIONAL工具（按需选择）
1. **FileSystemTool**
   - 文件系统操作
   - 方法：readFile, writeFile, appendToFile, listFiles, deleteFile, createDirectory
   - 安全：路径遍历防护

2. **DataBaseTool**
   - 数据库查询（仅SELECT）
   - 参数：sql
   - 安全：SQL注入防护

3. **EmailTool**
   - 邮件发送
   - 参数：to, subject, content
   - 异步执行

**工具实现方式**：
- 继承LangChain的StructuredTool基类
- 使用@tool装饰器定义元数据
- 集成自动类型检查和验证

### 6. 工具函数层 (app/utils/)

**职责**：提供通用工具函数

**模块**：
- id_generator.py - UUID生成
- date_utils.py - 日期时间处理
- helpers.py - JSON处理、字符串清理

## 数据流架构

### 1. 聊天流程

```
用户发送消息
    ↓
POST /api/chat-messages (with agentId)
    ↓
保存消息到数据库
    ↓
发送SSE事件（USER_MESSAGE）
    ↓
触发Agent处理（后台任务）
    ↓
创建Agent实例（JChatMindFactory）
    ↓
加载历史消息（最近20条）
    ↓
LangGraph循环启动
    ├─→ [Think节点]
    │    ↓
    │    LLM调用决策
    │    ↓
    │    保存ASSISTANT消息
    │    ↓
    │    发送SSE事件（ASSISTANT_MESSAGE）
    │
    └─→ [Execute节点] (如果有工具调用)
         ↓
         执行工具
         ↓
         保存TOOL消息
         ↓
         发送SSE事件（TOOL_RESULT）
         ↓
         步数+1
         ↓
         返回[Think]（如果未完成）
    ↓
Agent结束（调用terminate或达到最大步数）
```

### 2. 知识库流程

```
上传文档
    ↓
POST /api/documents/upload
    ↓
保存文件到本地存储
    ↓
创建Document记录
    ↓
解析文档内容（MarkdownParser）
    ↓
文本分块（chunk_size=1000, overlap=200）
    ↓
为每个分块生成嵌入
    ↓
存储到ChromaDB
    ↓
关联到KnowledgeBase
```

### 3. RAG检索流程

```
Agent调用KnowledgeTool
    ↓
RagService.similarity_search(kbId, query)
    ↓
为查询生成嵌入
    ↓
ChromaDB向量检索（top_k=5）
    ↓
返回相关文档片段
    ↓
片段作为上下文返回给LLM
```

## API接口规范

所有接口遵循统一响应格式：

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "data": null
}
```

### SSE事件格式

**用户消息事件**：
```json
{
  "event": "message",
  "data": {
    "type": "USER_MESSAGE",
    "message": {
      "id": "msg-id",
      "role": "user",
      "content": "用户输入"
    }
  }
}
```

**助手消息事件**：
```json
{
  "event": "message",
  "data": {
    "type": "ASSISTANT_MESSAGE",
    "message": {
      "role": "assistant",
      "content": "助手回复",
      "tool_calls": [
        {
          "name": "KnowledgeTool",
          "args": {...}
        }
      ]
    }
  }
}
```

**工具结果事件**：
```json
{
  "event": "message",
  "data": {
    "type": "TOOL_RESULT",
    "message": {
      "role": "tool",
      "content": "工具执行结果",
      "tool_name": "KnowledgeTool"
    }
  }
}
```

## 配置管理

### 环境变量（.env）

```env
# 数据库
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname

# LLM API密钥
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
ZHIPUAI_API_KEY=...

# 邮件配置
EMAIL_HOST=smtp.com
EMAIL_PORT=587
EMAIL_USERNAME=user@smtp.com
EMAIL_PASSWORD=password
EMAIL_FROM=user@smtp.com

# 应用配置
APP_NAME=chatmind-python
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true

# 存储路径
DOCUMENT_STORAGE_PATH=./data/documents
VECTOR_DB_PATH=./data/chroma

# Agent配置
MAX_AGENT_STEPS=20
MAX_CHAT_MESSAGES=20

# CORS
CORS_ORIGINS=*
```

## 部署架构

### 开发环境
```
用户
    ↓
FastAPI (uvicorn reload)
    ↓
PostgreSQL (本地)
    ↓
ChromaDB (本地文件)
```

### 生产环境
```
Nginx/Traefik
    ↓ (反向代理/SSL)
FastAPI (uvicorn workers)
    ├─→ PostgreSQL (RDS/托管)
    └─→ ChromaDB (持久化存储)
```

### Docker部署

**Dockerfile示例**：
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "app.main"]
```

**docker-compose.yml示例**：
```yaml
version: '3.8'

services:
  chatmind:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/chatmind
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=chatmind
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 性能优化

### 1. 数据库优化
- 使用连接池（SQLAlchemy Engine pool_size=10）
- 添加索引（session_id、agent_id、kb_id）
- 批量操作支持

### 2. 向量检索优化
- ChromaDB本地存储
- 嵌入缓存（TODO）
- 批量向量插入

### 3. API性能
- FastAPI异步支持
- CORS中间件优化
- 响应压缩（TODO）

### 4. Agent优化
- LangGraph检查点（状态持久化）
- 消息窗口限制（20条）
- 最大步数限制（20步）

## 安全考虑

### 1. 认证授权
- TODO: 添加JWT认证
- TODO: API密钥管理
- TODO: 用户权限控制

### 2. 输入验证
- Pydantic模型验证
- SQL注入防护（仅允许SELECT）
- 路径遍历防护（文件系统工具）

### 3. 数据加密
- TODO: 敏感字段加密
- HTTPS强制（生产环境）
- API密钥环境变量存储

### 4. 速率限制
- TODO: API速率限制
- TODO: 用户级别限制
- TODO: IP级别限制

## 监控和日志

### 日志级别
- DEBUG：开发环境详细日志
- INFO：生产环境运行日志
- ERROR：错误和异常日志

### 健康检查
```bash
GET /health
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "vector_store": "ok"
  }
}
```

### 指标（TODO）
- 请求数量
- 响应时间
- 错误率
- Agent执行时间

## 测试策略

### 单元测试
- Services层测试（test_services.py）
- Utils层测试

### A.P.I.测试
- 接口端点测试（test_api.py）
- 响应格式验证

### 集成测试（TODO）
- 完整聊天流程测试
- Agent工作流测试
- RAG检索测试

## 扩展性

### 添加新工具
1. 在`app/tools/`创建新工具类
2. 继承`Tool`基类
3. 实现业务逻辑
4. 在`ToolService`中注册

### 添加新LLM
1. 在`JChatMindFactory._create_llm()`添加逻辑
2. 配置API密钥
3. 更新文档

### 添加新存储后端
1. 实现新的`DocumentStorageService`
2. 更新`DocumentService`配置
3. 添加迁移

## 与Java版本对比

### 优势
1. **开发效率**：Python生态更丰富，LangChain社区活跃
2. **灵活性**：LangGraph提供更强大的状态管理
3. **可扩展性**：更容易添加自定义工具和LLM
4. **性能**：异步I/O处理更高效

### 功能对等
1. ✅ 所有API接口兼容
2. ✅ Agent行为一致
3. ✅ 工具系统功能相同
4. ✅ RAG检索能力相当
5. ✅ SSE实时推送支持

### 差异点
1. 数据库ORM：MyBatis vs SQLAlchemy
2. 状态管理：Spring AI ChatMemory vs LangGraph State
3. 事件系统：Spring Events vs asyncio Tasks
4. 向量库：自研 vs ChromaDB

## 未来改进

### 短期
1. 完善嵌入模型集成（BGE-M3）
2. 添加认证授权系统
3. 实现速率限制
4. 添加更多单元测试

### 中期
1. 支持多租户
2. 实现Agent版本管理
3. 添加流式响应
4. 支持插件系统

### 长期
1. 分布式部署支持
2. 实现Agent市场
3. 添加Web管理界面
4. 支持Agent协作

## 维护指南

### 依赖更新
```bash
# 更新依赖版本
pip list --outdated

# 更新requirements.txt
pip-compile requirements.in

# 安装更新
pip install -r requirements.txt --upgrade
```

### 数据库迁移
```bash
# 创建新迁移
alembic revision --autogenerate -m "description"

# 查看迁移历史
alembic history

# 回滚迁移
alembic downgrade -1

# 验证迁移
alembic check
```

### 问题排查
1. 检查日志：`tail -f logs/app.log`
2. 健康检查：`curl http://localhost:8000/health`
3. 数据库连接：`psql $DATABASE_URL`
4. 向量存储：检查`data/chroma/`目录

## 总结

ChatMind Python 实现了与 Java 版本功能等价的智能聊天系统，同时利用 Python 生态和 LangChain/LangGraph 的优势提供了更好的开发体验和扩展性。项目采用清晰的分层架构，各模块职责明确，便于维护和扩展。

通过保持 API 兼容性，可以无缝替换 Java 后端，为前端应用提供一致的服务接口。
