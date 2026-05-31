## 1. Middleware ABC 扩展

- [x] 1.1 新增 `after_llm(messages, response) -> response`
- [x] 1.2 新增 `after_tool(tool_name, tool_input, result) -> result`

## 2. Agent 调用点

- [x] 2.1 Agent._react_loop 中 LLM 调用后遍历 middleware.after_llm
- [x] 2.2 Agent._execute_tool 中工具调用后遍历 middleware.after_tool

## 3. 测试

- [x] 3.1 创建 `tests/test_middleware_after.py`：验证 after_llm/after_tool 被调用且可变换输出
