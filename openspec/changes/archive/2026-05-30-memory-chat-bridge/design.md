## Context

Memory 目前只有 `load_context() -> str`。Chat Model 引入消息类型后，Memory 与 Chat 体系不兼容——对话历史丢失了 role 信息。新增 `load_messages()` 让 Memory 直接产出消息列表。

## Goals / Non-Goals

**Goals:**
- Memory ABC 新增 `load_messages() -> List[BaseMessage]` 抽象方法
- 三种 Memory 实现各自实现 `load_messages()`
- 让 LLMChain 可以用消息列表而不是字符串加载历史

**Non-Goals:**
- 不删除 `load_context()` —— 保持向后兼容
- 不改 LLMChain 内部逻辑 —— v1 只加 Memory 侧
- 不实现 ChatLLMChain（消息原生 Chain）

## Decisions

### Decision 1: load_messages 返回 HumanMessage + AIMessage 交替序列

```python
# ConversationBufferMemory 内部存储:
# save_context({"question": "hi"}, {"text": "hello"})
# save_context({"question": "how are you?"}, {"text": "fine"})

# load_messages() 返回:
[
    HumanMessage("hi"),
    AIMessage("hello"),
    HumanMessage("how are you?"),
    AIMessage("fine"),
]
```

每个 save_context 对产生一对消息。

### Decision 2: SummaryMemory 的消息格式

```python
# ConversationSummaryMemory.load_messages() 返回:
[
    HumanMessage("Summary of conversation so far: ..."),
    HumanMessage(last_user_input),
    AIMessage(last_ai_output),
]
```

Summary 作为 HumanMessage（告诉模型"以下是之前对话的摘要"），最近一轮对话正常保留。

### Decision 3: load_messages 不含 SystemMessage

Memory 不负责生成 SystemMessage。SystemMessage 属于 prompt 设计，不属于对话历史。调用方在 ChatPromptTemplate 中添加 SystemMessage。
