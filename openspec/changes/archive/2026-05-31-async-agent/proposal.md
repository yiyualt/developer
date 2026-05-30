## Why

LLM.agenerate() 和 LLMChain.apply_async() 早已支持并发，但 Agent 只有同步 run()。用户无法并发运行多个 Agent 实例来处理多个问题。这是 async 路线的最后一块拼图——补齐 Agent 层的并发能力，与 LLMChain.apply_async() 对标。

## What Changes

- Agent 新增 `apply_async(questions: list[str]) -> list[str]`：用 `asyncio.gather` 并发运行多个问题，每个问题在独立 Agent 实例中执行，内部每步 ReAct 用 `llm.agenerate()` 替代 `llm.generate()`
- 对称于 `LLMChain.apply_async()`，遵循 v0.0.12 的最小 async 哲学

## Capabilities

### New Capabilities
- `async-agent`: Agent.apply_async(questions) 并发执行多个 Agent 运行，asyncio.gather 驱动

### Modified Capabilities
(无)

## Impact

- 修改文件：`langchain/agents/agent.py`（新增 apply_async 和 _arun_loop 内部方法）
- 无破坏性变更
