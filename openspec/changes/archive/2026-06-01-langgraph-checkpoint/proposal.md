## Why

当前 `invoke()` 只返回最终 state。很多场景需要中间状态的完整历史——调试、streaming、pause/resume。Checkpoint 在每次 superstep 后保存 state 快照，invoke 返回完整历史而非只剩最后一步。

## What Changes

- `invoke()` 返回类型从 `dict` 变为 `List[dict]`——每个 superstep 后的 state 快照列表
- 入口 state + 每次 superstep 后的 state 都记录
- 改名：`invoke()` → 返回快照列表；新增 `ainvoke()` 保持一致

## Capabilities

### New Capabilities
- `langgraph-checkpoint`：invoke() 返回完整 state 历史列表

### Modified Capabilities
- `langgraph-stategraph-channels`：CompiledGraph.invoke 返回值变更

## Impact

- **BREAKING**: `invoke()` 返回 `list[dict]` 而非 `dict`
- 修改：`langgraph/graph.py`
- 测试 + 文档
