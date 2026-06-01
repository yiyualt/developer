## Context

当前 StateGraph 只有固定边 `add_edge(from, to)`。Conditional edge 允许 from 节点指向一个 router 函数，router 检查 state 返回 key，key 通过 mapping 映射到实际目标节点。

## Design

### API

```python
graph.add_conditional_edges(
    "agent",                    # from_node
    lambda s: s.get("next"),   # router: (state) -> key
    {                           # mapping: key -> target_node
        "continue": "agent",    #  → 循环回 agent
        "end": END,             #  → 结束
    }
)
```

### 内部存储

```python
# StateGraph
self.conditional_edges: Dict[str, tuple] = {}
# {"agent": (router_func, {key: target})}
```

### CompiledGraph 执行

```python
# 原有：从固定边找下一批节点
if node_name in self._edges:
    for target in self._edges[node_name]:
        next_active.add(target)

# 新增：也检查 conditional edges
if node_name in self._conditional_edges:
    router, mapping = self._conditional_edges[node_name]
    key = router(state)
    target = mapping[key]
    if target != END:
        next_active.add(target)
```

### 混合使用

一个节点可以同时有固定边和 conditional 边——都会解析，结果合并到 next_active set。
