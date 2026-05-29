## Context

当前 Agent 和 Tool 各自独立：Agent 调用 Tool，但 Agent 不能被当作 Tool 被其他 Agent 调用。这破坏了组合性的递归原则——如果 Agent 本质上也是"接收输入、产生输出"，那它就是 Tool。本项目已经完成了 LLMChain、SequentialChain、Agent、Memory、Router、Streaming、Async 等特性，Agent 间的组合是最自然的下一步。

核心约束：
- Tool 的合约是 `name + description + run(input: str) -> str`
- Agent 的合约是 `run(question: str) -> str`
- 两种合约可以统一：`Agent.run(question)` = `Tool.run(input)` — 输入都是字符串，输出都是字符串

## Goals / Non-Goals

**Goals:**
- 实现 `AgentTool` 类：将一个 Agent 包装成 Tool，使其可被任何 Agent 作为工具调用
- 为 Agent 添加 `description` 属性，描述该 Agent 的专业能力范围
- AgentTool 完全符合 Tool ABC 合约，可在任何 Tool 出现的地方使用
- 被包装的 Agent 保持独立的 ReAct 循环、工具集和 Memory

**Non-Goals:**
- 不实现高层编排模式（MultiAgentOrchestrator、SequentialAgentChain）——这些留给后续版本
- 不实现 Agent 类型分类（ZeroShot / Conversational / PlanAndExecute）——后续版本
- 不实现任务分解（Plan-and-Execute）——后续版本
- 不改变现有 Agent 或 Tool 的公共 API

## Decisions

### Decision 1: AgentTool IS-A Tool（继承 Tool ABC）

**选择**：`class AgentTool(Tool)` — AgentTool 继承 Tool ABC。

**替代方案**：
- 组合方式（AgentTool 不继承 Tool，只是有相同的属性）：这违反了"Tool 能用处 AgentTool 就能用"的替换原则。继承保证类型兼容。
- 修改 Agent 让它直接实现 Tool 接口：混淆了 Agent 和 Tool 的职责。Agent 是"思考者"，Tool 是"执行者"——AgentTool 作为适配器桥接两种抽象。

**理由**：AgentTool IS-A Tool 意味着它自然兼容现有所有代码——Agent 的 `_tool_map`、Router 的目的地、任何期望 Tool 的地方。

### Decision 2: AgentTool 通过 `run(question)` 委托

**选择**：`AgentTool._run(input)` 调用 `self.agent.run(question=input)`。

**替代方案**：
- 通过 `run_with_log` 委托：增加复杂度，编排 Agent 不需要看到被包装 Agent 的内部推理
- 通过 `stream` 委托：不适合非流式场景

**理由**：AgentTool 是同步的、单次调用的委托。编排 Agent 只关心专家的最终答案，不关心中间推理。如果将来需要传递推理过程，可以添加一个 `return_full_log` 选项——但默认保持简单。

### Decision 3: Agent.description 参数设计

**选择**：在 Agent 构造函数中添加可选 `description` 参数，默认值为空字符串。

**理由**：当 Agent 被包进 AgentTool 时，编排 Agent 的 ReAct 提示中需要了解该专家的能力。"描述" 告诉编排者*这个专家能做什么*，这对正确的工具选择至关重要。

```python
class Agent:
    def __init__(self, ..., description: str = ""):
        self.description = description
```

AgentTool 使用 `agent.description` 作为默认的 Tool description，调用方也可以覆盖。

```python
class AgentTool(Tool):
    def __init__(self, name: str, agent: Agent, description: str = ""):
        self.name = name
        self.agent = agent
        self.description = description or agent.description or f"Delegates to {name} specialist agent"
```

### Decision 4: AgentTool 不共享 Memory

**选择**：被包装的 Agent 保持独立 Memory，不与编排 Agent 共享。

**理由**：共享 Memory 会打破组合性——被包装的 Agent 不知道自己在被另一个 Agent 调用，它就是一个普通的 Agent。如果有人需要共享 Memory，可以在构造时传入同一个 Memory 实例。默认为独立，按需共享。

### Decision 5: AgentTool 不触发编排 Agent 的回调

**选择**：AgentTool._run 内部调用 agent.run()，被包装 Agent 如果自己注册了回调，会正常触发。但调用 AgentTool 的编排 Agent 看到的只是一个普通的 Tool 调用事件（`on_tool_start` / `on_tool_end`）。

**理由**：AgentTool 实现了 Tool 合约，所以它从外部触发正确的 Tool 回调。被包装 Agent 内部的回调独立运作。这是自然的封装——编排者不需要知道 Tool 内部是否又嵌套了一个 Agent。

## Risks / Trade-offs

- **递归深度膨胀**：Agent → AgentTool → Agent → AgentTool → ... 可以无限嵌套。→ 不设硬性限制，LLM 的上下文窗口和 `max_iterations` 自然提供上限。如果真的发生无限递归，那是提示设计的问题，不是代码的问题。
- **错误传播**：被包装 Agent 的异常会向上传播到编排 Agent，编排 Agent 看到的是 Tool 执行失败。→ AgentTool 返回错误消息字符串（"Agent execution error: ..."），避免编排者崩溃。
- **提示膨胀**：每个 AgentTool 的描述会出现在编排 Agent 的 ReAct 提示中。如果有很多专家，提示会很长。→ 和普通 Tool 一样，这是调用方要管理的问题。
