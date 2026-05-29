## Why

AgentTool 让 Agent 可以当 Tool 用，但编排逻辑完全由用户手工拼装——为每个专精 Agent 创建 AgentTool，手动配置编排 Agent 的 tools 列表，自己构造 prompt。这些是重复模式，应该封装为开箱即用的编排类。这是"组合性"故事的收尾：从"可以组合"到"容易组合"。

## What Changes

- 新增 `MultiAgentOrchestrator`：接收一个 LLM 和一组专精 Agent，自动包装为 AgentTool，内部创建编排 Agent，`run(question)` 自动路由到最合适的专家
- 新增 `SequentialAgentChain`：接收一组 Agent，`run(question)` 依次执行，每个 Agent 的输出作为下一个的输入
- 两者都建立在 AgentTool 之上，是纯便利层

## Capabilities

### New Capabilities
- `agent-orchestration`: 两个编排模式——`MultiAgentOrchestrator`（路由分发，根据问题选择专家）和 `SequentialAgentChain`（串联管道，Agent 依次处理）

### Modified Capabilities
(无 — 纯增量)

## Impact

- 新增文件：`langchain/agents/orchestrator.py`（两个编排类）
- 修改文件：`langchain/agents/__init__.py`、`langchain/__init__.py`
- 无破坏性变更
