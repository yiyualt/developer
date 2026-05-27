## Context

LangChain 已有 PromptTemplate + LLM + LLMChain + OutputParser + SequentialChain + Agent(ReAct)。Agent 的 ReAct 循环每轮在 scratchpad 上追加 Thought+Action+Observation，多轮后 prompt 超长。LLMChain 和 SequentialChain 完全无状态，每次 run() 都是全新对话。

Memory 为 Chain 和 Agent 提供持久化的交互历史：保存每轮的 human/ai 对话，下次运行时自动加载到 prompt 中。

## Goals / Non-Goals

**Goals:**
- 实现 Memory ABC：定义 save_context, load_context, clear 接口
- 实现 ConversationBufferMemory：保存完整对话历史
- 实现 ConversationBufferWindowMemory：只保留最近 K轮
- LLMChain 支持可选 memory 参数，run/apply 自动交互
- Agent 支持可选 memory 参数

**Non-Goals:**
- 不实现长期存储（数据库持久化是后续版本）
- 不实现摘要式 Memory（SummaryMemory 是后续版本）
- 不实现向量检索式 Memory（VectorStoreMemory 是 RAG 版本的内容）
- 不实现跨 session 共享 Memory

## Decisions

### D1: Memory 接口设计

**选择**: `save_context(inputs: dict, outputs: dict)` + `load_context() -> str` + `clear()`
**理由**: save_context 接收 dict 格式（与 LLMChain 的 input/output 格式对齐），load_context 返回格式化好的字符串直接插入 prompt。接口极简但覆盖核心场景。
**替代**: save_context 接收两个 str（human_msg, ai_msg）— 丢失了 input 变量的结构化信息

### D2: 对话格式

**选择**: 每轮对话格式为 `"Human: {input}\nAI: {output}"`，多轮之间用换行拼接
**理由**: 最直观的对话格式，LLM 天然理解 Human/AI 角色标记。与 ReAct scratchpad 格式兼容。
**替代**: JSON 格式存储 — 更结构化但 LLM 不需要，徒增复杂度

### D3: WindowMemory 的 K 参数

**选择**: ConversationBufferWindowMemory 的 `k` 参数表示保留最近 K轮交互（K轮 = K个 Human+AI 对）
**理由**: "轮"比"条"更直观。一轮对话包含一个 human input 和一个 ai output。
**替代**: k 表示消息条数（容易混淆，一轮是两条消息）

### D4: Memory 与 LLMChain 的集成方式

**选择**: LLMChain.__init__ 新增可选 `memory` 参数。run() 调用时：先 `memory.load_context()` 追加到 prompt，执行完后 `memory.save_context()` 保存本轮 input/output
**理由**: 自动集成，用户不需要手动管理 history。memory=None 时行为与之前完全一致。
**替代**: 手动传 history 参数给 run() — 用户负担太重

## Risks / Trade-offs

- [Memory 字符串过长] → ConversationBufferWindowMemory 提供截断方案，后续可加 SummaryMemory
- [Memory 只保存在内存中] → 当前版本只在 Python 进程内存中，session 结束后丢失 → 后续版本加持久化
- [Memory 与 Agent scratchpad 重复] → Agent 的 ReAct scratchpad 是单次循环的临时历史，Memory 是跨 run() 的持久历史，两者互补而非重复