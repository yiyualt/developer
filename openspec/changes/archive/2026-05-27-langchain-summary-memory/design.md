## Context

ConversationBufferMemory 存全部历史，ConversationBufferWindowMemory 只返回最近 K 轮。
两者都没有"压缩"能力 — Buffer 无限增长，Window 丢弃旧信息。
真实 LangChain 早期引入 ConversationSummaryMemory 作为第三种选择：
用 LLM 把旧对话压缩为摘要，保留关键信息同时控制长度。

Agent 当前只保存 Final Answer 到 Memory，中间步骤（Thought/Action/Observation）
丢失了。后续对话看不到推理过程，可能重复调用相同 Tool。

## Goals / Non-Goals

**Goals:**
- ConversationSummaryMemory: LLM 压缩对话历史为摘要
- Agent 中间步骤存入 Memory（不只是 Final Answer）
- 与现有 LLMChain 和 Agent 无缝集成

**Non-Goals:**
- VectorStoreRetrieverMemory（Tool 结果存向量库）— 需要 RAG 稳定后再做
- ConversationEntityMemory（实体提取）— 后续版本
- 摘要持久化到磁盘 — 先做内存存储

## Decisions

### Decision 1: 摘要触发时机

**选择**: 每次 `save_context()` 时，如果已有 2+ 轮完整对话且当前有摘要，
就把最新的轮次追加到摘要中，用 LLM 重新压缩。保留最近 1 轮完整对话不压缩。
**替代**: 固定轮次阈值（每 N 轮压缩一次）
**理由**: 每次追加式压缩比"攒一堆再压缩"更稳定。
摘要始终包含历史要点，加上最近一轮的完整对话作为上下文。
这与真实 LangChain 早期 SummaryMemory 的设计一致。

### Decision 2: Agent 中间步骤格式

**选择**: Agent 保存完整 ReAct 过程到 Memory，格式为：
`AI: Thought: ... Action: tool[input] Observation: result Final Answer: answer`
**替代**: 只保存 Observation 和 Final Answer
**理由**: 保留完整推理过程让后续对话能理解 Agent 做了什么。
只存 Final Answer 会丢失"Agent 调用了哪个 Tool、得到了什么结果"的信息。

### Decision 3: SummaryMemory 需要 LLM 参数

**选择**: ConversationSummaryMemory 构造时需要传入 `llm` 参数
**替代**: 不传 LLM，用固定的字符串截断代替摘要
**理由**: 真正的摘要需要 LLM 理解语义并保留关键信息。
字符串截断只是粗暴砍掉尾部，丢失信息量大。
传入 LLM 是合理的依赖 — Memory 的压缩能力来自于 LLM。

## Risks / Trade-offs

- **[摘要质量]** → LLM 摘要可能丢失细节 → 摘要 prompt 需要强调保留关键事实和决策
- **[额外 LLM 调用]** → 每次 save_context 多一次 LLM call → 这是 SummaryMemory 的固有代价，真实 LC 也是这样
- **[摘要漂移]** → 多次压缩后摘要可能偏离原始内容 → 保留最近 1 轮完整对话作为锚点