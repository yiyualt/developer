## Context

当前 LangChain 有 9 个模块（PromptTemplate, LLM, Chain, Agent, Memory, Retrieval, Router, OutputParser, Tool），所有组件的执行流程都是黑盒。LLMChain.run() 内部经历 memory 加载、prompt 构建、LLM 调用、memory 保存、output 解析，但开发者无法观测中间步骤。Agent 的 ReAct 循环更复杂——多步推理、工具调用、观察收集——只能通过 run_with_log() 事后回顾。真实 LangChain 在 2023 年初引入 Callback 系统，我们同步这一演进。

## Goals / Non-Goals

**Goals:**
- 定义 CallbackHandler ABC，统一生命周期事件钩子接口
- 在 LLMChain、Agent、Tool 的关键执行节点触发回调事件
- 提供内置 StdOutCallbackHandler，打印执行日志到终端
- 不改变现有 API 返回值，回调是纯附加行为

**Non-Goals:**
- 不做 callback 向下传递（SequentialChain 传给子 Chain）——留作下一步演进
- 不做异步 callback 或 streaming callback
- 不做 CallbackManager 或 callback 优先级/过滤
- 不做 tracing ID 或分布式追踪（那是更后面的演进）
- 不做 LangSmith 风格的云端追踪平台集成

## Decisions

### Decision 1: Handler 模式而非事件流

**选择**: CallbackHandler ABC + 实例方法钩子（路线 A）
**替代**: EventEmitter / 事件流模式（路线 B）

**理由**: 与真实 LangChain 的历史演进一致。Handler 模式最朴素：每个组件维护一个 callbacks 列表，在关键节点逐个调用 handler 的方法。简单、直接、易理解。事件流模式更"现代"，但不符合这个阶段的设计哲学——先把最简版做好，复杂度自然演化。

### Decision 2: callbacks 作为组件构造参数

**选择**: `LLMChain(llm=..., callbacks=[handler])` — 构造时传入
**替代**: `chain.run(question=..., callbacks=[handler])` — 每次调用时传入

**理由**: 构造时传入更符合 LangChain 的风格（LLMChain 的 llm、memory 都是构造参数）。对于需要固定回调的场景（如日志、追踪），构造时传入更方便。但 run() 时传入对于临时调试也有价值——这个版本先只支持构造参数，run() 时传入留作演进。

### Decision 3: 事件粒度——先覆盖核心路径

**选择**: 8 个核心钩子：on_llm_start/end, on_chain_start/end, on_tool_start/end, on_agent_action/finish, + on_error
**替代**: 更多细粒度钩子（on_memory_load/save, on_prompt_format, on_output_parse）

**理由**: 先覆盖最主要的执行路径（LLM 调用、Chain 执行、Tool 调用、Agent 推理）。Memory 和 Prompt 是内部步骤，暂不暴露钩子——保持最小化，后续按需添加。

### Decision 4: StdOutCallbackHandler 输出格式

**选择**: 简洁的行式输出 `[LLMChain] Start: {question}` / `[LLMChain] End: {answer}`
**替代**: JSON 结构化输出

**理由**: 人类可读的行式输出更适合终端调试。JSON 输出留给未来的 TracingHandler 或 LangSmith 集成。

## Risks / Trade-offs

- **[回调列表逐个调用可能有性能影响]** → 针数少（通常 1-2 个 handler），影响可忽略。未来如果 handler 多了，需要考虑过滤或异步
- **[callback 不向下传递导致 SequentialChain 内子 Chain 不可观测]** → 这一步先接受这个限制，下一步演进解决
- **[handler 方法签名需要考虑未来扩展]** → 用 `**kwargs` 传递额外信息，避免频繁改签名