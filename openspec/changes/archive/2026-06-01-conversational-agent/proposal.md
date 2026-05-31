## Why

当前 Agent 用普通字符串工作——PromptTemplate 产字符串，Memory.load_context() 返回字符串，System prompt 被手动拼进模板。v0.0.17-0.0.18 引入了消息类型和 Memory 消息接口，v0.0.19 做了 Self-Correction，但它们还没有被任何 Agent 真正使用。ConversationalAgent 是第一个原生于消息类型的 Agent——用 ChatPromptTemplate 设 SystemMessage，用 Memory.load_messages() 加载历史，用 generate_messages() 调用 LLM。之前所有基础设施的汇聚点。

## What Changes

- 新增 `ConversationalAgent` 类：原生消息型多轮对话 Agent
- ReAct 循环用 `generate_messages()` 替代 `generate()`
- System prompt 用 `SystemMessage`，对话历史用 `Memory.load_messages()`
- 继承 `CallbackMixin`，支持 `callbacks`、`apply_async()`

## Capabilities

### New Capabilities
- `conversational-agent`: 消息原生型 Agent——用 ChatPromptTemplate + Memory 消息 + generate_messages() 实现多轮对话

### Modified Capabilities
(无 — 现有 Agent 不动)

## Impact

- 新增文件：`langchain/agents/conversational.py`
- 修改文件：`langchain/agents/__init__.py`、`langchain/__init__.py`
- 无破坏性变更
