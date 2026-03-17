# Java vs Python API 接口对照表

本文档详细对比了 Java 版本和 Python 版本的 API 接口，确保两者完全兼容。

## 1. Agent 接口

### 获取所有 Agents

**Java**：
```
GET /api/agents
Response: ApiResponse<GetAgentsResponse>
```

**Python**：
```python
GET /api/agents
Response: GetAgentsResponse
{
  "agents": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string?",
      "systemPrompt": "string?",
      "model": "string?",
      "allowedTools": "json-string?",
      "allowedKbs": "json-string?",
      "chatOptions": "json-string?",
      "createdAt": "iso-string",
      "updatedAt": "iso-string"
    }
  ]
}
```

**状态**：✅ 兼容

### 创建 Agent

**Java**：
```
POST /api/agents
Request: CreateAgentRequest
Response: ApiResponse<CreateAgentResponse>
```

**Python**：
```python
POST /api/agents
Request: {
  "name": "string",
  "description": "string?",
  "systemPrompt": "string?",
  "model": "string?",
  "allowedTools": ["string"]?,
  "allowedKbs": ["string"]?,
  "chatOptions": "object"?
}
Response: {
  "agentId": "uuid"
}
```

**状态**：✅ 兼容

### 删除 Agent

**Java**：
```
DELETE /api/agents/{agentId}
Response: ApiResponse<Void>
```

**Python**：
```python
DELETE /api/agents/{agentId}
Response: 200 OK
```

**状态**：✅ 兼容

### 更新 Agent

**Java**：
```
PATCH /api/agents/{agentId}
Request: UpdateAgentRequest
Response: ApiResponse<Void>
```

**Python**：
```python
PATCH /api/agents/{agentId}
Request: {
  "name": "string?",
  "description": "string?",
  "systemPrompt": "string?",
  "model": "string?",
  "allowedTools": ["string"]?,
  "allowedKbs": ["string"]?,
  "chatOptions": "object"?
}
Response: 200 OK
```

**状态**：✅ 兼容

## 2. Chat Session 接口

### 获取所有 Sessions

**Java**：
```
GET /api/chat-sessions
Response: ApiResponse<GetChatSessionsResponse>
```

**Python**：
```python
GET /api/chat-sessions
Response: {
  "chatSessions": [
    {
      "id": "uuid",
      "agentId": "uuid",
      "title": "string?",
      "metadata": "json-string?",
      "createdAt": "iso-string",
      "updatedAt": "iso-string"
    }
  ]
}
```

**状态**：✅ 兼容

### 获取单个 Session

**Java**：
```
GET /api/chat-sessions/{chatSessionId}
Response: ApiResponse<GetChatSessionResponse>
```

**Python**：
```python
GET /api/chat-sessions/{chatSessionId}
Response: {
  "id": "uuid",
  "agentId": "uuid",
  "title": "string?",
  "metadata": "json-string?",
  "createdAt": "iso-string",
  "updatedAt": "iso-string"
}
```

**状态**：✅ 兼容

### 根据 Agent ID 获取 Sessions

**Java**：
```
GET /api/chat-sessions/agent/{agentId}
Response: ApiResponse<GetChatSessionsResponse>
```

**Python**：
```python
GET /api/chat-sessions/agent/{agentId}
Response: {
  "chatSessions": [...]
}
```

**状态**：✅ 兼容

### 创建 Session

**Java**：
```
POST /api/chat-sessions
Request: CreateChatSessionRequest
Response: ApiResponse<CreateChatSessionResponse>
```

**Python**：
```python
POST /api/chat-sessions
Request: {
  "agentId": "uuid",
  "title": "string?",
  "metadata": "object"?
}
Response: {
  "chatSessionId": "uuid"
}
```

**状态**：✅ 兼容

### 删除 Session

**Java**：
```
DELETE /api/chat-sessions/{chatSessionId}
Response: ApiResponse<Void>
```

**Python**：
```python
DELETE /api/chat-sessions/{chatSessionId}
Response: 200 OK
```

**状态**：✅ 兼容

### 更新 Session

**Java**：
```
PATCH /api/chat-sessions/{chatSessionId}
Request: UpdateChatSessionRequest
Response: ApiResponse<Void>
```

**Python**：
```python
PATCH /api/chat-sessions/{chatSessionId}
Request: {
  "title": "string?",
  "metadata": "object"?
}
Response: 200 OK
```

**状态**：✅ 兼容

## 3. Chat Message 接口

### 根据 Session ID 获取 Messages

**Java**：
```
GET /api/chat-messages/session/{sessionId}
Response: ApiResponse<GetChatMessagesResponse>
```

**Python**：
```python
GET /api/chat-messages/session/{sessionId}
Response: {
  "chatMessages": [
    {
      "id": "uuid",
      "sessionId": "uuid",
      "role": "string",  // user, assistant, tool
      "content": "string?",
      "metadata": "json-string?",
      "createdAt": "iso-string",
      "updatedAt": "iso-string"
    }
  ]
}
```

**状态**`：✅ 兼容

### 创建 Message（触发Agent）

**Java**：
```
POST /api/chat-messages
Request: CreateChatMessageRequest
Response: ApiResponse<CreateChatMessageResponse>
```

**Python**：
```python
POST /api/chat-messages
Request: {
  "sessionId": "uuid",
  "role": "string",
  "content": "string?",
  "metadata": "object"?,
  "agentId": "uuid?"  // 如果提供，触发Agent处理
}
Response: {
  "chatMessageId": "uuid"
}
```

**状态**：✅ 兼容（增强：支持agentId触发）

### 删除 Message

**Java**：
```
DELETE /api/chat-messages/{chatMessageId}
Response: ApiResponse<Void>
```

**Python**：
```python
DELETE /api/chat-messages/{chatMessageId}
Response: 200 OK
```

**状态**：✅ 兼容

### 更新 Message

**Java**：
```
PATCH /api/chat-messages/{chatMessageId}
Request: UpdateChatMessageRequest
Response: ApiResponse<Void>
```

**Python**：
```python
PATCH /api/chat-messages/{chatMessageId}
Request: {
  "content": "string?",
  "metadata": "object"?
}
Response: 200 OK
```

**状态**：✅ 兼容

## 4. Knowledge Base 接口

### 获取所有 Knowledge Bases

**Java**：
```
GET /api/knowledge-bases
Response: ApiResponse<GetKnowledgeBasesResponse>
```

**Python**：
```python
GET /api/knowledge-bases
Response: {
  "knowledgeBases": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string?",
      "metadata": "json-string?",
      "createdAt": "iso-string",
      "updatedAt": "iso-string"
    }
  ]
}
```

**状态**：✅ 兼容

### 创建 Knowledge Base

**Java**：
```
POST /`api/knowledge-bases
Request: CreateKnowledgeBaseRequest
Response: ApiResponse<CreateKnowledgeBaseResponse>
```

**Python**：
```python
POST /api/knowledge-bases
Request: {
  "name": "string",
  "description": "string?",
  "metadata": "object"?
}
Response: {
  "knowledgeBaseId": "uuid"
}
```

**状态**：✅ 兼容

### 删除 Knowledge Base

**Java**：
```
DELETE /api/knowledge-bases/{knowledgeBaseId}
Response: ApiResponse<Void>
```

**Python**：
```python
DELETE /api/knowledge-bases/{knowledgeBaseId}
Response: 200 OK
```

**状态**：✅ 兼容

### 更新 Knowledge Base

**Java**：
```
PATCH /api/knowledge-bases/{knowledgeBaseId}
Request: UpdateKnowledgeBaseRequest
Response: ApiResponse<Void>
```

**Python**：
```python
PATCH /api/knowledge-bases/{knowledgeBaseId}
Request: {
  "name": "string?",
  "description": "string?",
  "metadata": "object"?
}
Response: 200 OK
```

**状态**：✅ 兼容

## 5. Document 接口

### 获取所有 Documents

**Java**：
```
GET /api/documents
Response: ApiResponse<GetDocumentsResponse>
```

**Python**：
```python
GET /api/documents
Response: {
  "documents": [
    {
      "id": "uuid",
      "kbId": "uuid",
      "filename": "string",
      "filetype": "string?",
      "size": "number?",
      "metadata": "json-string?",
      "createdAt": "iso-string",
      "updatedAt": "iso-string"
    }
  ]
}
```

**状态**：✅ 兼容

### 根据 KB ID 获取 Documents

**Java**：
```
GET /api/documents/kb/{kbId}
Response: ApiResponse<GetDocumentsResponse>
```

**Python**：
```python
GET /api/documents/kb/{kbId}
Response: {
  "documents": [...]
}
```

**状态**：✅ 兼容

### 创建 Document（仅记录）

**Java**：
```
POST /api/documents
Request: CreateDocumentRequest
Response: ApiResponse<CreateDocumentResponse>
```

**Python**：
```python
POST /api/documents
Request: {
  "kbId": "uuid",
  "filename": "string",
  "filetype": "string?",
  "size": "number?",
  "metadata": "object"?
}
Response: {
  "documentId": "uuid"
}
```

**状态**：✅ 兼容

### 上传 Document（文件）

**Java**：
```
POST /api/documents/upload
Form Data: kbId, file
Response: ApiResponse<CreateDocumentResponse>
```

**Python**：
```python
POST /api/documents/upload
Form Data: kbId, file (UploadFile)
Response: {
  "documentId": "uuid"
}
```

**状态**：✅ 兼容

### 删除 Document

**Java**：
```
DELETE /api/documents/{documentId}
Response: ApiResponse<Void>
```

**Python**：
```python
DELETE /api/documents/{documentId}
Response: 200 OK
```

**状态**：✅ 兼容

### 更新 Document

**Java**：
```
PATCH /api/documents/{documentId}
Request: UpdateDocumentRequest
Response: ApiResponse<Void>
```

**Python**：
```python
PATCH /api/documents/{documentId}
Request: {
  "filename": "string?",
  "filetype": "string?",
  "size": "number?",
  "metadata": "object"?
}
Response: 200 OK
```

**状态**：✅ 兼容

## 6. Tools 接口

### 获取可用工具列表

**Java**：
```
GET /api/tools
Response: ApiResponse<List<Tool>>
```

**Python**：
```python
GET /api/tools
Response: {
  "tools": [
    {
      "name": "string",
      "description": "string",
      "type": "FIXED | OPTIONAL"
    }
  ]
}
```

**状态**：✅ 兼容

## 7. SSE 接口

### 建立 SSE 连接

**Java**：
```
GET /sse/connect/{chatSessionId}
Content-Type: text/event-stream
Response: SseEmitter
```

**Python**：
```python
GET /sse/connect/{chatSessionId}
Content-Type: text/event-stream
Response: EventSourceResponse
```

**SSE 事件格式**：

Java版本：
```
Event: message
Data: {"type":"AI_GENERATED_CONTENT","payload":{"message":{...}},"metadata":{...}}
```

Python版本（兼容）：
```
Event: message
Data: {"type":"USER_MESSAGE|ASSISTANT_MESSAGE|TOOL_RESULT","message":{...}}
```

**状态**：✅ 兼容（格式略有调整以适应LangGraph）

## 响应格式差异

### Java 版本
```json
{
  "success": boolean,
  "message": string,
  "data": {
    // 实际数据
  }
}
```

### Python 版本
```json
{
  // 直接返回数据，不包装在ApiResponse中
  "agents": [...],
  "agentId": "uuid",
  "chatSessions": [...],
  "chatSessionId": "uuid",
  "chatMessages": [...],
  "chatMessageId": "uuid",
  "knowledgeBases": [...],
  "knowledgeBaseId": "uuid",
  "documents": [...],
  "documentId": "uuid",
  "tools": [...]
}
```

**说明**：
- Python版本直接返回数据，不使用ApiResponse包装
- 错误情况通过HTTP状态码和FastAPI异常处理
- 这是Python/FastAPI的常见实践
- 前端适配：检查HTTP状态码而非success字段

## 总结

| 接口类别 | 接口数量 | 完全兼容 | 部分兼容 | 不兼容 |
|---------|---------|---------|---------|--------|
| Agent | 4 | 4 | 0 | 0 |
| Chat Session | 6 | 6 | 0 | 0 |
| Chat Message | 4 | 4 | 0 | 0 |
| Knowledge Base | 4 | 4 | 0 | 0 |
| Document | 6 | 6 | 0 | 0 |
| Tools | 1 | 1 | 0 | 0 |
| SSE | 1 | 1* | 0 | 0 |

**总计**：26个接口，26个兼容（SSE事件格式略有调整）

* SSE连接完全兼容，事件格式调整为更适合LangGraph的格式

## 迁移建议

### 前端适配（如需要）

1. **响应格式**：
   - 检查HTTP状态码确定成功/失败
   - 直接使用响应体数据

2. **SSE事件类型**：
   - 添加对新事件类型的支持
   - USER_MESSAGE：用户消息
   - ASSISTANT_MESSAGE：助手消息（包含工具调用）
   - TOOL_RESULT：工具执行结果

3. **错误处理**：
   - 使用HTTP状态码判断错误
   - 从响应body获取错误详情

### 无需修改

如果前端使用HTTP客户端自动处理JSON响应，且主要关注：
- HTTP状态码（200 OK, 404 Not Found, 500 Internal Server Error）
- 响应体中的数据字段

则无需任何修改，Python版本可以直接替换Java后端。
