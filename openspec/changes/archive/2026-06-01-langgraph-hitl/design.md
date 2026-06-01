## Design

```python
class StateGraph:
    def compile(self, interrupt_before=None, interrupt_after=None):
        return CompiledGraph(..., interrupt_before=interrupt_before or [])

class CompiledGraph:
    def __init__(self, ..., interrupt_before):
        self._interrupt_before = set(interrupt_before)

    def stream(self, input_state, config=None):
        ...
        for i in range(limit):
            if not active: break

            # Check interrupt-before the active nodes
            if self._interrupt_before & active:
                yield self._read_state()  # yield current state as checkpoint
                break

            # ... normal superstep execution ...
```

### 使用流程

```python
app = graph.compile(interrupt_before=["approval"])

# Step 1: stream until interrupt
for s in app.stream({"input": "delete all data"}):
    print(s)  # yields states until "approval" node

# Step 2: last snapshot is the checkpoint
checkpoint = s  # {"input": ..., "pending_action": "delete"}

# Step 3: human modifies state
checkpoint["approved"] = True

# Step 4: resume from checkpoint
result = app.invoke(input_state=checkpoint)
```
