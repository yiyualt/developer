## Context

当前 Agent 用 prompt 文本告诉 LLM 有哪些工具，LLM 输出文本，代码正则解析出工具名和参数。Function Calling 把工具定义作为 API 参数发送，LLM 原生返回结构化 JSON。

## Goals / Non-Goals

**Goals:**
- `Tool.to_json_schema()` → OpenAI function 格式的 JSON Schema
- `OpenAI.generate_with_tools(messages, tools)` → 发送工具定义，返回结构化响应
- `FunctionCallingAgent` → 用原生 function calling 替代字符串解析

**Non-Goals:**
- 不修改现有 Agent 类
- 不实现并行 tool calls（v1 只支持单工具调用）

## Decisions

### Decision 1: JSON Schema 格式

遵循 OpenAI Function Calling 格式：

```python
{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Performs arithmetic calculations.",
        "parameters": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "The expression to evaluate, e.g. '2+3'"
                }
            },
            "required": ["input"]
        }
    }
}
```

Tool ABC 提供默认实现：参数是 `{"input": {"type": "string"}}` 的单字符串。工具可重写来定义结构化参数。

### Decision 2: generate_with_tools 返回格式

```python
def generate_with_tools(self, messages_list, tools):
    """
    Returns: List[dict] with:
        - content: str or None (LLM text response)
        - tool_calls: list of dicts with name, arguments
    """
    completion = self._client.chat.completions.create(
        model=...,
        messages=[...],
        tools=[t.to_json_schema() for t in tools],
    )
    choice = completion.choices[0]
    return [{
        "content": choice.message.content,
        "tool_calls": [
            {"name": tc.function.name, "arguments": tc.function.arguments}
            for tc in (choice.message.tool_calls or [])
        ] if choice.message.tool_calls else []
    }]
```

### Decision 3: FunctionCallingAgent 循环

```
1. 构建消息列表：[SystemMessage, ...history, HumanMessage(question)]
2. 调用 generate_with_tools(messages, tools)
3. 如果返回 content → 最终答案
4. 如果返回 tool_calls → 执行工具，Observation 作为 AIMessage，循环回到步骤 2
5. 最多 max_iterations 次
```

与 ReAct 的关键区别：不需要 Thought/Action/Observation 字符串，整个循环是消息驱动的。

### Decision 4: 独立类

`FunctionCallingAgent` 不继承 Agent 或 ConversationalAgent。它是独立的，因为核心循环完全用 API 的 function calling 能力，不需要 output parser、prompt template 等。

## Risks / Trade-offs

- **模型兼容性**：function calling 需要模型支持，glm-5.1 的兼容性需要实测验证
- **单工具**：v1 只处理单个 tool_call，多工具并行调用留给后续版本
