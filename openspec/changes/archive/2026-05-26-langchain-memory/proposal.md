## Why

Agent 的 ReAct 循环每轮追加 Thought+Action+Observation 到 prompt，多轮后 prompt 超长且无法截断。LLMChain 和 SequentialChain 也没有对话历史感知能力。Memory 让 Chain 和 Agent 能记住之前的交互，既解决 prompt 过长问题，也为多轮对话场景提供基础。

## What Changes

- 新增 `Memory` ABC：定义内存接口（save_context, load_context, clear）
- 新增 `ConversationBufferMemory`：保存完整对话历史（human + ai 交替）
- 新增 `ConversationBufferWindowMemory`：只保留最近 K轮对话（截断旧历史）
- LLMChain 新增可选 `memory` 参数：每次 run/apply 前自动加载历史，执行后自动保存
- Agent 新增可选 `memory` 参数：ReAct 循环中使用 memory 提供历史上下文

## Capabilities

### New Capabilities
- `memory`: Memory ABC 及 ConversationBufferMemory、ConversationBufferWindowMemory 实现

### Modified Capabilities
- `llm-chain`: LLMChain 新增可选 memory 参数，run/apply 自动与 memory 交互
- `agent`: Agent 新增可选 memory 参数
- `doc-content-structure`: Notes 增加 memory-design 页面，Examples 增加 memory-example 页面

## Impact

- 新增模块：`langchain/memory/`
- 修改模块：`langchain/chains/llm_chain.py`、`langchain/agents/agent.py`
- 包导出更新：`langchain/__init__.py`
- 文档更新：API reference、Notes、Examples