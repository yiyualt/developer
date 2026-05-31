## 1. Runnable 基础设施

- [x] 1.1 创建 `langchain/runnables.py`：Runnable ABC（invoke + __or__）、RunnableSequence

## 2. 组件实现 Runnable

- [x] 2.1 PromptTemplate 实现 Runnable.invoke（委托给 format）
- [x] 2.2 LLM ABC 实现 Runnable.invoke（委托给 generate）
- [x] 2.3 OutputParser ABC 实现 Runnable.invoke（委托给 parse）

## 3. 导出

- [x] 3.1 在 `langchain/__init__.py` 中导出 Runnable、RunnableSequence

## 4. 测试

- [x] 4.1 创建 `tests/test_lcel.py`：验证 pipe、RunnableSequence、end-to-end prompt | llm | parser

## 5. 文档

- [x] 5.1 创建 `docs/notes/lcel-philosophy.rst` + 示例，更新 toctree
