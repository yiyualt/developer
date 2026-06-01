## Design

```python
def invoke(self, input_state: dict, config: dict = None) -> list:
    snapshots = [dict(input_state)]
    
    for i in range(limit):
        if not active:
            break
        # ... superstep execution ...
        snapshots.append(self._read_state())
    else:
        raise RecursionError(...)
    
    return snapshots
```

### 返回值变化

```
之前:  invoke() → {"x": 3, "result": "done"}
现在:  invoke() → [{"x": 0}, {"x": 1}, {"x": 2}, {"x": 3, "result": "done"}]
                                     ↑ 每次 superstep 后的状态
```
