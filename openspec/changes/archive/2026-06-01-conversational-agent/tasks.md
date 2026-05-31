## 1. ConversationalAgent 实现

- [x] 1.1 创建 `langchain/agents/conversational.py`：实现 ConversationalAgent 类 — 消息型 ReAct 循环，用 SystemMessage + Memory.load_messages() + generate_messages()，支持 callbacks

## 2. 导出集成

- [x] 2.1 在 `langchain/agents/__init__.py` 和 `langchain/__init__.py` 中导出

## 3. 测试

- [x] 3.1 创建 `tests/test_conversational_agent.py`：验证消息构建、多轮对话、工具使用

## 4. 文档

- [x] 4.1 创建 `docs/notes/conversational-agent-philosophy.rst` + `docs/examples/conversational-agent-example.rst`，更新 toctree
