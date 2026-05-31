## 1. Middleware ABC + before_llm

- [x] 1.1 Middleware ABC 新增 `before_llm(messages) -> messages` 默认透传

## 2. SummarizationMiddleware

- [x] 2.1 在 `middleware.py` 中新增 `SummarizationMiddleware` 类

## 3. Agent 调用 before_llm

- [x] 3.1 Agent._react_loop 中 LLM 调用前遍历 middleware.before_llm

## 4. 测试

- [x] 4.1 创建 `tests/test_summarization_middleware.py`

## 5. 文档

- [x] 5.1 更新 `docs/examples/hitl-example.rst` 添加 Summarization 示例
