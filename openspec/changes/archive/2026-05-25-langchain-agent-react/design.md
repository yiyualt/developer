## Context

LangChain 已有 PromptTemplate + LLM + LLMChain + OutputParser + SequentialChain。SequentialChain 是固定顺序的多步执行，但真实场景需要 LLM 自主决策：根据当前观察选择下一步行动。ReAct（Reasoning + Acting）模式由 Yao et al. 2022 提出，核心思想是 LLM 在循环中交替进行 Thought（思考）和 Action（执行工具），观察工具返回的 Observation，再继续思考直到得出 Final Answer。

当前架构中 LLMChain 是单步执行，SequentialChain 是固定多步。Agent 引入了一个全新的执行模型：while 循环 + 动态工具选择。

## Goals / Non-Goals

**Goals:**
- 实现 Agent 类：ReAct 模式的 while 循环执行
- 实现 Tool ABC：定义工具接口（name, description, run）
- 实现内置 Tool：Calculator、Search（模拟）、Python REPL
- Agent 每轮从 LLM 输出中提取 Thought + Action，调用对应 Tool，将 Observation 回填
- Agent 在收到 Final Answer 或达到 max_iterations 时终止循环

**Non-Goals:**
- 不实现多 Agent 协作
- 不实现 Agent 的长期记忆（Memory 是后续版本）
- 不实现工具学习（Agent 自动发现新工具）
- 不实现 Plan-and-Solve 模式（只做 ReAct）

## Decisions

### D1: ReAct prompt 格式

**选择**: 使用固定格式的 ReAct prompt，要求 LLM 输出遵循 `Thought: ... Action: ...` 或 `Thought: ... Final Answer: ...` 格式
**理由**: 结构化输出让 AgentOutputParser 可以可靠提取 Thought 和 Action。ReAct 论文验证了这种格式能引导 LLM 进行有效推理。
**替代**: 自由格式输出 + 复杂 NLP 解析（不稳定，依赖 LLM 的格式遵守能力）

### D2: Action 格式

**选择**: `Action: tool_name[action_input]` — 工具名 + 方括号内的输入
**理由**: 最简洁的格式，容易解析。ReAct 论文原始格式。
**替代**: JSON 格式 Action（更结构化但 prompt 更复杂，LLM 更容易出错）

### D3: Tool 接口设计

**选择**: Tool ABC 包含 `name`（str）、`description`（str）、`run(input: str) -> str` 三个要素
**理由**: name 用于 Action 解析匹配，description 写入 ReAct prompt 让 LLM 知道可用工具，run 执行工具。接口极简，但足够让 Agent 工作。
**替代**: Tool.run() 返回 dict（过度设计，LLM 只需要把 Observation 作为文本读入）

### D4: Agent 的执行模型

**选择**: `Agent.run(question: str) -> str` 返回 Final Answer（裸值），同时 `Agent.run_with_log() -> dict` 返回完整执行日志
**理由**: run() 简洁返回最终答案方便大多数使用场景，run_with_log() 供调试和审计用。
**替代**: 只返回日志 dict（日常使用太复杂）

## Risks / Trade-offs

- [LLM 不遵循 Thought/Action 格式] → AgentOutputParser 需要容错处理，解析失败时把整个输出作为 Thought 继续
- [工具执行出错] → Tool.run() 返回错误信息字符串作为 Observation，Agent 可以在下一轮尝试不同工具
- [循环无限] → max_iterations 硬上限（默认 5），超过时返回最近一轮的 Thought 作为答案
- [ReAct prompt 过长] → 每轮追加 Thought+Action+Observation，多轮后 prompt 超长 → 后续版本可加 Memory 截断