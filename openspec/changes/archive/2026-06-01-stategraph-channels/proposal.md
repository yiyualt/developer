## Why

当前 StateGraph 用 `state.update(node_output)` 合并状态——纯 dict overwrite。LangGraph 的核心架构是 **Channels + Reducers**：每个状态字段有独立的"如何合并"策略。messages 是 append（不是 replace），count 是 add（不是 overwrite）。没有 Reducer，多节点并行更新会互相覆盖，循环图的状态管理也会出错。这是 LangGraph 和普通 DAG 的最根本区别——必须在 v0.0.1 就做对。

## What Changes

- 新增 `Channel` 类：封装一个状态字段 + reducer 策略
- Reducer 策略：`replace`（默认）、`append`、`add`
- `StateGraph` 用 `TypedDict` 风格的 schema 定义状态形状 + reducer
- `CompiledGraph.invoke` 通过 reducer 合并节点输出（不再用 bare dict update）

## Capabilities

### New Capabilities
- `stategraph-channels`: StateGraph + Channel + Reducer（append/replace/add）

### Modified Capabilities
(无 — 新建包)

## Impact

- 新建文件：`langgraph/graph.py`（重写）、`langgraph/channels.py`（新）
- 删除：当前 `langgraph/graph.py` 的 bare dict update 实现
