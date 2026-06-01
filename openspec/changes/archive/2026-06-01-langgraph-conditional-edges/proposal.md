## Why

当前 StateGraph 只有 `add_edge(from, to)`——固定路由。Agent 循环需要"LLM 调用后根据结果决定继续还是结束"——这需要动态路由：根据当前 state 决定下一个节点。Conditional Edges 让图能分支、能循环、能基于状态做决策。

## What Changes

- StateGraph 新增 `add_conditional_edges(from_node, router, mapping)`：router 检查 state 返回一个 key，mapping 把 key 映射到目标节点
- CompiledGraph 在 superstep 转换时，对 conditional edge 调用 router 决定 actual target

## Capabilities

### New Capabilities
- `langgraph-conditional-edges`: StateGraph.add_conditional_edges 方法

### Modified Capabilities
- `langgraph-stategraph-channels`: CompiledGraph 执行逻辑支持 conditional edge

## Impact

- 修改：`langgraph/graph.py`
- 测试 + 文档
