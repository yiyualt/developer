## Why

当前 Agent 靠解析字符串 `"Action: calculator[2+3]"` 来调用工具。这是 2022 年 ReAct 的做法——LLM 输出自由文本，代码用正则提取工具名和参数。2023 年 3 月 OpenAI 推出了 Function Calling：直接把工具定义发给 API，LLM 返回结构化的 JSON `{"name": "calculator", "arguments": {...}}`。这是 Agent 调用工具的正确方式——不再解析字符串，不再猜格式，不再出"解析错误"。真实 LangChain 在 Agent 之后、LCEL 之前的里程碑就是 Function Calling。

## What Changes

- Tool ABC 新增 `to_json_schema()`：返回 OpenAI Function 格式的 JSON Schema
- OpenAI 新增 `generate_with_tools(messages, tools)`：把工具定义发给 API，返回 `{content, tool_calls}`
- 新增 `FunctionCallingAgent`：用原生 Function Calling 替代字符串解析的 ReAct 循环

## Capabilities

### New Capabilities
- `function-calling`: Tool 提供 JSON Schema，LLM 通过 API 原生返回 tool_calls，Agent 不再解析字符串

### Modified Capabilities
- `tool`: Tool ABC 新增 `to_json_schema()` 方法

## Impact

- 新增：`langchain/agents/function_calling.py`
- 修改：`langchain/tools/base.py`（新增 to_json_schema）、`langchain/llms/openai.py`（新增 generate_with_tools）
- 无破坏性变更
