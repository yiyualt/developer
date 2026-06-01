## Why

invoke() 收集所有 snapshots 最后返回——适合批处理。实时场景需要逐步推送：聊天界面想看到每步状态，调试想看到图怎么跑的。stream() 用 Python generator 逐步 yield snapshot，不改 invoke 行为。

## What Changes

- CompiledGraph 新增 `stream(input_state, config)` 生成器
- 每个 superstep 后 yield 当前 state snapshot
- invoke() 保持不变，内部由 stream + list() 实现

## Capabilities

### New Capabilities
- `langgraph-streaming`: CompiledGraph.stream() 逐步 yield state snapshots

## Impact

- 修改：`langgraph/graph.py`（+15 行）
- 测试 + 文档
