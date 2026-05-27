## Context

LangChain 已有 LLMChain、SequentialChain、RetrievalChain、Agent — 所有执行路径都是固定的。
Router Chain 引入动态选择：根据输入内容，由 LLM 决定走哪条路径。

项目中已有 JsonOutputParser（解析 LLM 输出为 JSON），已有 Agent（动态选择 Tool）。
Router Chain 与 Agent 共享"Dynamic Option Injection"设计模式 —
将可用选项（destinations / tools）的 name+description 自动注入 prompt，让 LLM 选择。

## Goals / Non-Goals

**Goals:**
- RouterChain ABC 定义路由接口
- LLMRouterChain 用 LLM + JsonOutputParser 做决策
- ChainDestination 封装 name + description + chain 实例
- Router 可路由到任意 Chain 类型（LLMChain, RetrievalChain, Agent）
- 必须有 default destination 作为 fallback
- SingleRoute — 选一个 chain 执行（不做 MultiRoute）
- Prompt 从 destinations 自动构建（不手写）

**Non-Goals:**
- MultiRoute（并行执行多条链）— 后续版本
- EmbeddingRouterChain（相似度路由）— 后续版本
- 路由到 SequentialChain — 需要更复杂的输入映射，后续考虑

## Decisions

### Decision 1: JsonOutputParser 复用

**选择**: Router 输出用 JSON 格式 `{"chain": "retrieval"}`，用已有的 JsonOutputParser 解析
**替代**: 专用 RouterOutputParser / 纯字符串匹配
**理由**: 项目已有 JsonOutputParser，无需发明新组件。
JSON 格式比裸字符串更可靠（LLM 对 JSON 格式遵从度高），
且保留 reason 字段便于调试路由决策。

### Decision 2: Router 可路由到任意 Chain

**选择**: RouterChain.route() 返回 ChainDestination，其 chain 可以是任何类型
**替代**: 只路由到 LLMChain（MultiPromptChain 方式）
**理由**: 项目已有 RetrievalChain 和 Agent，只路由到 LLMChain 价值有限。
ABC 设计允许任意 Chain 类型，但示例先用 MultiPrompt 演示（不同 prompt 的 LLMChain），
保留历史感的同时不限制架构扩展。

### Decision 3: 必须指定 default destination

**选择**: LLMRouterChain 构造时必须指定 default_destination
**替代**: 抛异常 / 重试
**理由**: LLM 路由输出可能无法解析或匹配失败，
fallback chain 保障用户体验，教学场景下最友好。
真实 LangChain 早期也是 default fallback 方式。

### Decision 4: SingleRoute

**选择**: Router 只选一个 destination 执行
**替代**: MultiRoute（选多个并行执行）
**理由**: 还原早期 LC 的做法。MultiRoute 是后来的演进。
SingleRoute 更简单，且避免了多条链结果合并的复杂性。

## Risks / Trade-offs

- **[LLM 路由准确性]** → LLM 可能选错 chain → default_destination 兜底，但不保证最优路径
- **[额外 LLM 调用]** → 每次路由多一次 LLM call → 延迟增加。EmbeddingRouter 后续优化
- **[JSON 解析失败]** → JsonOutputParser strict 模式下抛异常 → 使用 non-strict 模式 + fallback
- **[Router 与 Agent 语义重叠]** → 都是"LLM 动态选择" → Router 选 chain（宏观），Agent 选 tool（微观），粒度不同