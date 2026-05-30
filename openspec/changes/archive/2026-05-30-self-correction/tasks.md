## 1. LLMCorrector

- [x] 1.1 创建 `langchain/agents/self_correct.py`：实现 `LLMCorrector` 类——`check(question, answer)` 用 LLM 判断答案是否合格

## 2. SelfCorrectingAgent

- [x] 2.1 同文件实现 `SelfCorrectingAgent` 类——包装 Agent，添加 检查→不通过则重试 循环，max_retries 上限

## 3. 导出集成

- [x] 3.1 在 `langchain/agents/__init__.py` 和 `langchain/__init__.py` 中导出两个类

## 4. 测试

- [x] 4.1 创建 `tests/test_self_correct.py`：验证首次通过、失败重试、max_retries 耗尽

## 5. 文档

- [x] 5.1 创建 `docs/notes/self-correction-philosophy.rst` 并更新 toctree
- [x] 5.2 创建 `docs/examples/self-correction-example.rst` 并更新 toctree
