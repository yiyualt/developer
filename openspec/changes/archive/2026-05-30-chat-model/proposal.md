## Why

当前系统的数据流是纯字符串：`PromptTemplate` → 字符串 → `LLM.generate()` → 硬编码 `role: user`。System prompt 被手动拼进模板，多轮对话靠 Memory 拼字符串。但底层 API 本身就是 Chat Completions（支持 system/user/assistant 角色），我们只是没用上。引入消息类型让 prompt 从"一个字符串"变成"结构化的消息序列"——这是 LangChain 从 Completion 时代进入 Chat 时代的标志。

## What Changes

- 新增消息类型：`BaseMessage`（ABC）、`SystemMessage`、`HumanMessage`、`AIMessage`
- 新增 `ChatPromptTemplate`：接收消息模板列表，`format()` 返回消息列表而非字符串
- `OpenAI` 扩展 `generate_messages()`：接收消息列表，正确传递每个消息的 role
- 保持向后兼容：`LLM.generate(strings)` 不变，`generate_messages` 是新增接口

## Capabilities

### New Capabilities
- `chat-model`: 消息类型体系（SystemMessage/HumanMessage/AIMessage）和 ChatPromptTemplate，让 prompt 从字符串升级为结构化消息序列

### Modified Capabilities
(无 — 纯增量，LLM.generate 保持不变)

## Impact

- 新增文件：`langchain/schema.py`（新增消息类型）、`langchain/prompts/chat.py`（ChatPromptTemplate）
- 修改文件：`langchain/llms/openai.py`（新增 `generate_messages`）、`langchain/__init__.py`（导出）
- 无破坏性变更
