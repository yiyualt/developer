## Context

当前 Tool 创作必须写子类。`@tool` 是纯语法糖——用装饰器消除样板代码，不改变 Tool ABC 的行为或合约。

## Goals / Non-Goals

**Goals:**
- 实现 `@tool` 装饰器：`@tool` 放在函数上，返回一个 Tool 实例
- name = 函数名，description = docstring（第一行）
- 返回值是 `FunctionTool` 实例（Tool 的动态子类）
- `@tool` 也接受显式参数覆盖 name/description

**Non-Goals:**
- 不实现 `ToolKit`（工具集合）——后续版本
- 不修改 Tool ABC
- 不支持异步函数——v1 只支持同步

## Decisions

### Decision 1: 装饰器支持两种调用方式

```python
# 方式 1: 无参数（name/description 自动取）
@tool
def calculator(input: str) -> str:
    """Performs arithmetic calculations."""
    return str(eval(input))

# 方式 2: 带参数（覆盖 name/description）
@tool(name="calc", description="Custom description")
def calculator(input: str) -> str:
    return str(eval(input))
```

**实现方式**：检查第一个参数是否为可调用对象。如果是 → 方式 1（直接装饰）；如果不是 → 方式 2（返回装饰器）。

### Decision 2: FunctionTool 是内部类

```python
class FunctionTool(Tool):
    """Internal Tool subclass created by @tool decorator."""
    def __init__(self, func, name=None, description=None):
        super().__init__()
        self.name = name or func.__name__
        self.description = description or (func.__doc__ or "").strip().split("\n")[0]
        self._func = func

    def _run(self, input: str) -> str:
        return self._func(input)
```

**理由**：不暴露 FunctionTool 给用户。用户只需要知道 `@tool` 返回一个 Tool。

### Decision 3: description 取 docstring 第一行

`description` 自动取函数 docstring 的第一个非空行，避免完整多行 docstring 塞进 ReAct 提示。

## Risks / Trade-offs

- **有状态工具**：`@tool` 包装的函数不持有实例状态。如果需要状态，用户仍应使用 Tool 子类。→ 这是设计上的权衡：简单工具用 `@tool`，复杂工具用子类。
