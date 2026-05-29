## Why

LangChain 已经有了 Agent（能推理、能调用 Tool）和 Tool（单一能力单元），但 Agent 和 Tool 之间还有一道墙——Agent 调用 Tool，但 Agent 本身不能被其他 Agent 当作 Tool 来调用。打破这道墙意味着：Agent 可以委派子任务给专精 Agent，实现递归组合。这是"组合性"故事的关键一步——从 v0.0.12 的单 Agent 孤岛迈入 Agent 间的协作。

## What Changes

- 新增 `AgentTool` 类：将一个 Agent 实例包装成 Tool，使其可被其他 Agent 调用
- Agent 新增 `description` 属性：描述 Agent 的能力范围，供编排 Agent 在 ReAct 推理中选择合适的专家
- AgentTool IS-A Tool：完全兼容现有 Tool 接口，可在任何使用 Tool 的地方使用
- AgentTool 内部通过调用包装 Agent 的 `run()` 方法执行委派

## Capabilities

### New Capabilities
- `agent-tool`: AgentTool 将一个 Agent 包装成 Tool，实现 Agent 间的递归组合——编排 Agent 可以将专精 Agent 作为 Tool 调用

### Modified Capabilities
- `agent`: Agent 新增 `description` 属性，描述该 Agent 的能力范围

## Impact

- 新增文件：`langchain/agents/tool.py`（AgentTool 类）
- 修改文件：`langchain/agents/agent.py`（Agent 添加 description）、`langchain/agents/__init__.py`、`langchain/__init__.py`
- 无破坏性变更：所有现有 API 保持不变，AgentTool 是纯增量
