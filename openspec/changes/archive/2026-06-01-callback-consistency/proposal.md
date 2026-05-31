## Why

Agent、LLMChain、Tool 都实现了 callbacks 参数和 `_fire()` 钩子机制，但后加的 PlanAndExecuteAgent、MultiAgentOrchestrator、SequentialAgentChain、SelfCorrectingAgent、LLMCorrector、AgentTool 完全没有。用户无法在不同组件上注册统一回调。这是不一致性的根因——不是有人用 print，而是新代码没接入钩子系统。

## What Changes

- 提取 `CallbackMixin`：把三处重复的 `_fire()` 逻辑集中到一个 mixin
- AgentTool 继承 CallbackMixin，代理内部回调
- PlanAndExecuteAgent、MultiAgentOrchestrator、SequentialAgentChain、SelfCorrectingAgent 接受 callbacks 参数并接入钩子
- LLMCorrector 接受 callbacks 参数（作为独立非 Agent 组件）
- 消除 Agent._execute_tool 中与 Tool.run() 重复的 on_tool_start/end 回调

## Capabilities

### New Capabilities
- `callback-consistency`: 所有 Agent/编排/修正组件统一接受 callbacks 参数，通过 CallbackMixin 提供一致的 `_fire()` 行为

### Modified Capabilities
- `agent`: Agent._execute_tool 不再重复 fire on_tool_start/end（由 Tool 层负责）
- `callback`: 新增 CallbackMixin 作为可复用基类

## Impact

- 新增：`langchain/callbacks/mixin.py`（CallbackMixin）
- 修改：`langchain/callbacks/__init__.py`、`langchain/tools/base.py`、`langchain/agents/agent.py`、`langchain/chains/llm_chain.py`、`langchain/agents/plan_execute.py`、`langchain/agents/orchestrator.py`、`langchain/agents/self_correct.py`、`langchain/agents/tool.py`、`langchain/__init__.py`
- 无破坏性变更（对外 API 是新增 callbacks 参数，现有用法不变）
