## 1. 消息类型

- [x] 1.1 在 `langchain/schema.py` 中新增 `BaseMessage`、`SystemMessage`、`HumanMessage`、`AIMessage` dataclass

## 2. ChatPromptTemplate

- [x] 2.1 创建 `langchain/prompts/chat.py`：实现 `ChatPromptTemplate`，接收消息模板列表，`format()` 对所有消息的 content 执行变量替换

## 3. OpenAI generate_messages

- [x] 3.1 在 `langchain/llms/openai.py` 中新增 `generate_messages(messages_list)` 方法，正确传递每个消息的 role

## 4. 导出集成

- [x] 4.1 在 `langchain/__init__.py` 中导出消息类型、ChatPromptTemplate

## 5. 测试

- [x] 5.1 创建 `tests/test_chat_model.py`：验证消息类型、ChatPromptTemplate、generate_messages

## 6. 文档

- [x] 6.1 创建 `docs/notes/chat-model-philosophy.rst` 并更新 toctree
- [x] 6.2 创建 `docs/examples/chat-model-example.rst` 并更新 toctree
