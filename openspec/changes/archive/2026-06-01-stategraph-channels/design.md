## Context

LangGraph 的状态更新不是简单的 dict.update。每个字段有独立的 reducer 控制合并行为——这使得多节点并行更新和循环图中的状态累积都能正确工作。

## Design

### Channel + Reducer

```python
def replace(old, new): return new         # 默认：覆盖
def append(old, new): return old + new    # 消息：追加
def add(old, new): return old + new       # 计数：求和
```

### State Schema

用户用带 `Annotated` 的 TypedDict 风格定义 state：

```python
class AgentState:
    messages: Annotated[list, append]    # 追加
    count: Annotated[int, add]           # 求和
    name: str                            # 默认 replace
```

`StateGraph.__init__` 解析 schema，为每个字段创建 Channel。

### Channel 执行

```python
class Channel:
    def __init__(self, reducer=replace):
        self.reducer = reducer
        self.value = None

    def update(self, new_value):
        if self.value is None:
            self.value = new_value
        else:
            self.value = self.reducer(self.value, new_value)
```

### StateGraph 初始化

```python
class StateGraph:
    def __init__(self, state_schema):
        self.channels = {}
        for key, typ in state_schema.__annotations__.items():
            reducer = get_reducer_from_annotation(typ)  # extract from Annotated
            self.channels[key] = Channel(reducer)
```

### Node 输出合并

```python
# 节点返回 {"messages": [msg1], "count": 2}
for key, val in node_output.items():
    if key in self.channels:
        self.channels[key].update(val)
```

### START sentinel + invoke

保持不变——StateGraph.add_node, add_edge, compile 的 API 不变，只改内部状态合并逻辑。
