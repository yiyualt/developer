## Context

当前 Agent 纯字符串工作。ConversationalAgent 用消息类型重写整个链路。

## Goals / Non-Goals

**Goals:**
- ReAct 循环用消息替代字符串
- System prompt → `SystemMessage`
- 对话历史 → `Memory.load_messages()`
- LLM 调用 → `OpenAI.generate_messages()`
- 继承 `CallbackMixin`，支持 `callbacks`

**Non-Goals:**
- 不修改现有 Agent 类
- 不修改 Memory 或消息类型
- 不实现多模态

## Decisions

### Decision 1: 独立类，不继承 Agent

**选择**：`ConversationalAgent` 是独立类，不复用 Agent。

**理由**：ReAct 循环的核心不同——Agent 用 `generate(str)`，ConversationalAgent 用 `generate_messages([[msg]])`。合并为一个类会引入 if-else 分支，增加复杂度。

### Decision 2: 消息构建顺序

```
load_messages() → HumanMessage(user_input)  → (scratchpad 追加在最后)
```

1. 如果有 Memory，`load_messages()` 返回历史消息
2. 加上 `HumanMessage(user_input)` — 当前问题
3. ReAct 循环中，每步的 Thought/Action/Observation 追加为消息

### Decision 3: generate_messages 而非 generate

```python
# Agent（当前）:
response = self.llm.generate([字符串prompt])[0]

# ConversationalAgent:
messages = [SystemMessage(...)] + history + [HumanMessage(q)] + scratchpad
response = self.llm.generate_messages([messages])[0]
```

每个消息的 role 被正确传递到 API。

### Decision 4: API 一致

`run(question)` / `run_with_log(question)` / `apply_async(questions)` — 与 Agent API 对称。

## Risks / Trade-offs

- **generate_messages 只在 OpenAI 上**：LLM ABC 没有抽象 generate_messages。→ 调用方必须用 OpenAI 或其子类。
- **Memory 必须支持 load_messages()**：ConversationalAgent 调用 `memory.load_messages()`，如果 Memory 不支持会 AttributeError。→ 所有现有 Memory 已实现 load_messages()（v0.0.18）。
