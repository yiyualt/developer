## Context

Agent 循环本身有 `max_iterations`，但这只限制 ReAct 循环轮数，不限制具体调用次数。Runtime Middleware 提供更精细的控制。

## Design

### ModelCallLimitMiddleware

在 `before_llm` 中计数。当超出限制时，返回一个仅含 `HumanMessage("Limit exceeded")` 的消息列表——这会让 LLM 看到限制信息但无法继续。

```python
class ModelCallLimitMiddleware(Middleware):
    def __init__(self, max_calls=10):
        self.max_calls = max_calls
        self._count = 0

    def before_llm(self, messages):
        self._count += 1
        if self._count > self.max_calls:
            return [HumanMessage("Model call limit exceeded.")]
        return messages
```

### ToolCallLimitMiddleware

在 `before_tool` 中计数。支持全局限制和逐工具限制。

```python
class ToolCallLimitMiddleware(Middleware):
    def __init__(self, max_calls=None, per_tool=None):
        # max_calls: int — global limit across all tools
        # per_tool: dict[str, int] — per-tool limits
        self.max_calls = max_calls
        self.per_tool = per_tool or {}
        self._counts: dict[str, int] = {}

    def before_tool(self, tool_name, tool_input):
        self._counts[tool_name] = self._counts.get(tool_name, 0) + 1

        if tool_name in self.per_tool:
            if self._counts[tool_name] > self.per_tool[tool_name]:
                return (False, f"Tool '{tool_name}' limit exceeded.")
        if self.max_calls and sum(self._counts.values()) > self.max_calls:
            return (False, "Global tool call limit exceeded.")

        return (True, tool_input)
```
