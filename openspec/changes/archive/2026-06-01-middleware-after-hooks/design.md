## Context

before_tool / before_llm 控制输入。after_llm / after_tool 观察和变换输出——在 LLM 响应返回给 Agent 之前，在工具结果返回给 LLM 之前，插入处理逻辑。

## Design

### 两个新钩子

```python
def after_llm(self, messages: list, response: str) -> str:
    """Called after each LLM call. Return (possibly transformed) response."""
    return response

def after_tool(self, tool_name: str, tool_input: str, result: str) -> str:
    """Called after each tool execution. Return (possibly transformed) result."""
    return result
```

### Agent 调用点

```python
# _react_loop — after LLM:
response = llm.generate([prompt])[0]
for mw in self.middleware:
    response = mw.after_llm(call_messages, response)

# _execute_tool — after tool:
result = tool.run(action.tool_input)
for mw in self.middleware:
    result = mw.after_tool(action.tool, action.tool_input, result)
```

### 解锁的 Middleware

```
after_llm:   Model Fallback（响应为空/错误时切模型）
             Model Retry（重试失败的 LLM 调用）

after_tool:  Tool Retry（工具返回错误时重试）
```
