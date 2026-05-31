## Context

当前 `Tool.requires_approval` + `Agent.approver` 把审批配置拆在两边。官方把所有配置集中在 `HumanInTheLoopMiddleware(interrupt_on={...})` 中，Agent 只负责遍历 middleware 列表。

## Goals / Non-Goals

**Goals:**
- `Middleware` ABC：`before_tool(tool_name, input) -> (approved, modified_input)`
- `HumanInTheLoopMiddleware`：`interrupt_on` dict 配置哪些工具需要审批
- Agent 用 `middleware: List[Middleware]` 替代 `approver`

**Non-Goals:**
- 不实现 `after_tool`、`before_llm`、`after_llm` 钩子（v1 只有 before_tool）

## Decisions

### Decision 1: Middleware ABC

```python
class Middleware(ABC):
    @abstractmethod
    def before_tool(self, tool_name: str, tool_input: str) -> tuple:
        """Return (should_proceed: bool, modified_input: str)."""
        return (True, tool_input)
```

### Decision 2: HumanInTheLoopMiddleware

```python
class HumanInTheLoopMiddleware(Middleware):
    def __init__(self, interrupt_on=None, approver=None):
        # interrupt_on: dict[str, bool | dict]
        #   {"send_email": True, "read_email": False}
        #   {"send_email": {"allowed_decisions": ["approve","edit","reject"]}}
        # approver: callable for actually asking the human
```

### Decision 3: Agent._execute_tool 遍历 middleware

```python
def _execute_tool(self, action):
    tool = self._tool_map.get(action.tool)
    if tool is None:
        return f"Error: tool '{action.tool}' not found"
    
    for mw in self.middleware:
        proceed, modified = mw.before_tool(action.tool, action.tool_input)
        if not proceed:
            return f"Tool '{action.tool}' rejected by middleware."
        action.tool_input = modified
    
    return tool.run(action.tool_input)
```
