## Why

SequentialChain 让多个 LLMChain 按固定顺序串联执行，但真实场景中 LLM 需要自主决定下一步做什么——根据观察到的结果动态选择工具、决定是否继续。这就是 ReAct（Reasoning + Acting）模式：LLM 思考 → 选择工具 → 执行 → 观察结果 → 再思考，循环直到得出最终答案。

## What Changes

- 新增 `Agent` 类：基于 ReAct 模式的自主执行循环
- 新增 `Tool` ABC：定义工具接口（name, description, run）
- 新增几个内置 Tool 实现：`CalculatorTool`、`SearchTool`（模拟）、`Python REPL Tool`
- Agent 在每次循环中调用 LLM 生成 "Thought + Action"，解析 Action 调用对应 Tool，将 Observation 回填到 prompt，继续循环
- 新增 `AgentOutputParser`：从 LLM 输出中提取 Thought/Action/Observation 结构
- LLMChain 无变更，Agent 是独立模块

## Capabilities

### New Capabilities
- `agent`: ReAct 模式的自主 Agent，包含循环执行、Thought/Action/Observation 解析、工具调用
- `tool`: Tool ABC 及内置工具实现（Calculator, Search, Python REPL）

### Modified Capabilities
- `doc-content-structure`: Notes 增加 agent-design 页面，Examples 增加 agent-example 页面

## Impact

- 新增模块：`langchain/agents/`、`langchain/tools/`
- 包导出更新：`langchain/__init__.py`、`langchain/agents/__init__.py`、`langchain/tools/__init__.py`
- 文档更新：API reference、Notes、Examples
- Agent 依赖 LLMChain 的 prompt 组合能力，但不修改 LLMChain 本身