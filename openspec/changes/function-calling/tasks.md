## 1. Tool JSON Schema

- [x] 1.1 在 `langchain/tools/base.py` 的 Tool ABC 中新增 `to_json_schema()` 方法，返回 OpenAI function 格式

## 2. OpenAI generate_with_tools

- [x] 2.1 在 `langchain/llms/openai.py` 中新增 `generate_with_tools(messages_list, tools)` 方法

## 3. FunctionCallingAgent

- [x] 3.1 创建 `langchain/agents/function_calling.py`：实现 FunctionCallingAgent，用 generate_with_tools 替代字符串解析

## 4. 导出集成

- [x] 4.1 在 `langchain/agents/__init__.py` 和 `langchain/__init__.py` 中导出

## 5. 测试

- [x] 5.1 创建 `tests/test_function_calling.py`：验证 JSON Schema 格式、generate_with_tools、agent 循环

## 6. 文档

- [x] 6.1 创建 `docs/notes/function-calling-philosophy.rst` 并更新 toctree
- [x] 6.2 创建 `docs/examples/function-calling-example.rst` 并更新 toctree
