## 1. Memory ABC

- [x] 1.1 在 `langchain/memory/base.py` 的 Memory ABC 中新增 `load_messages()` 抽象方法

## 2. Memory 实现

- [x] 2.1 在 `langchain/memory/buffer.py` 中实现 `ConversationBufferMemory.load_messages()` —— 返回交替的 HumanMessage/AIMessage
- [x] 2.2 在 `langchain/memory/buffer_window.py` 中实现 `ConversationBufferWindowMemory.load_messages()` —— 受窗口限制
- [x] 2.3 在 `langchain/memory/summary.py` 中实现 `ConversationSummaryMemory.load_messages()` —— 摘要 + 最近轮次

## 3. 测试

- [x] 3.1 创建 `tests/test_memory_chat.py`：验证三种 Memory 的 load_messages 返回值

## 4. 文档

- [x] 4.1 更新 `docs/notes/memory-design.rst`：添加 load_messages 说明
