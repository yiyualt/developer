## Why

ConversationBufferMemory 存储完整对话历史，但随着对话轮次增加，
`load_context()` 返回的字符串越来越长，最终超出 prompt 容量限制。
ConversationSummaryMemory 用 LLM 定期压缩历史为摘要，
保留关键信息的同时控制 prompt 长度，是真实 LangChain 最早引入的
解决 Buffer 无限增长问题的方案。

## What Changes

- 新增 **ConversationSummaryMemory** — 当对话历史超过阈值时，用 LLM 压缩为摘要
- 更新 **Agent** — 中间步骤（Thought/Action/Observation）存入 Memory，让后续对话可见推理过程

## Capabilities

### New Capabilities
- `summary-memory`: LLM 压缩对话历史为摘要，控制 prompt 长度

### Modified Capabilities
- `memory`: 新增一种 Memory 实现类型
- `agent`: 中间步骤存入 Memory，不只是保存 Final Answer

## Impact

- 新增 `langchain/memory/summary.py` — ConversationSummaryMemory
- 更新 `langchain/agents/agent.py` — `_run_loop` 中存入完整推理过程
- 更新 `langchain/__init__.py` — 导出 ConversationSummaryMemory
- 新增 Sphinx 文档