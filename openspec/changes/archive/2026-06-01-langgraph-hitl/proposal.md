## Why

Checkpoint + Streaming 已就绪。HITL 只需要加一个中断机制：在特定节点前暂停，让人类检查/修改状态，然后从中断点恢复。这是 LangGraph 的核心差异化能力——不同于 LangChain 的工具级拦截，这里是图引擎级的暂停+恢复。

## What Changes

- `compile(interrupt_before: list[str])` — 标记哪些节点前要中断
- stream() 遇到中断节点时立即停止，当前状态通过 snapshot 暴露给调用方
- 调用方修改 snapshot 后，用 `invoke(input_state=snapshot)` 从中断点恢复

## Capabilities

### New Capabilities
- `langgraph-hitl`: compile 接受 interrupt_before，stream 支持暂停+恢复

## Impact

- 修改：`langgraph/graph.py`
- 测试 + 文档
