## Why

当前 `invoke()` 的 `max_iterations=100` 是硬编码。用户无法控制循环上限，超限时静默截断而非报错。需要可配置的 recursion limit。

## What Changes

- `invoke(state, config=None)` 接受 `config={"recursion_limit": 25}`
- 默认 limit 从 100 降到 25（更安全）
- 超限抛出 `RecursionError` 并包含当前 state 信息

## Capabilities

### New Capabilities
- `langgraph-recursion-limit`：invoke() 的 config 参数，recursion_limit 可配置

### Modified Capabilities
- `langgraph-stategraph-channels`：CompiledGraph.invoke 签名变更

## Impact

- 修改：`langgraph/graph.py`
- 测试 + 文档
