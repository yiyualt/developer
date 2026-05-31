## Why

对话越来越长时，Agent 的 context 膨胀——所有历史消息都在 prompt 里。SummarizationMiddleware 在每次 LLM 调用前检查消息长度，当超出阈值时自动压缩旧消息为摘要，保持 context 在可控范围内。这是 Middleware ABC 的第一个"读写"能力扩展：不是拦截工具调用，而是变换 LLM 输入。

## What Changes

- Middleware ABC 新增 `before_llm(messages) -> messages` 钩子——默认透传
- Agent._react_loop 中在 LLM 调用前遍历 middleware 调用 before_llm
- 新增 `SummarizationMiddleware`：当消息总字符数超过 `max_tokens * 4`（近似）时，用 LLM 压缩前半部分消息为一个摘要消息，插入到对话中

## Capabilities

### New Capabilities
- `summarization-middleware`: Middleware 的 `before_llm` 钩子 + SummarizationMiddleware 自动压缩对话历史

### Modified Capabilities
- `middleware-system`: Middleware ABC 新增 `before_llm` 钩子
- `agent`: Agent 循环在 LLM 调用前遍历 middleware.before_llm

## Impact

- 修改：`langchain/agents/middleware.py`（ABC + SummarizationMiddleware）、`langchain/agents/agent.py`（调用 before_llm）
- 无破坏性变更
