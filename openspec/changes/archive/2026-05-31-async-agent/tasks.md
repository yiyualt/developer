## 1. Async Agent 实现

- [x] 1.1 在 Agent 中新增 `_arun_loop(question)` — 异步 ReAct 循环，每个 LLM 调用使用 `await llm.agenerate()`
- [x] 1.2 新增 `apply_async(questions)` — 用 asyncio.gather 并发执行多个 _arun_loop

## 2. 测试

- [x] 2.1 创建 `tests/test_async_agent.py`：验证并发执行、结果顺序、ReAct 循环使用 agenerate

## 3. 文档

- [x] 3.1 更新 `docs/examples/async-example.rst` 添加 Agent.apply_async 示例
