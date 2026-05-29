## Context

当前的 Agent 执行 ReAct 循环：Thought → Action → Observation → ... → Final Answer。这个模式适合"回答问题"，但不适合"完成目标"——一个需要多步骤才能完成的任务。Plan-and-Execute 是一种不同于 ReAct 的 Agent 策略：先将目标分解为计划，再逐步执行。

PlanAndExecuteAgent 不继承 Agent 类——它有不同的执行模型（计划→执行 vs. 推理→行动循环）。但它可以直接使用 LLM 和 Tool/AgentTool，复用现有抽象。

## Goals / Non-Goals

**Goals:**
- 实现 `PlanAndExecuteAgent` 类：`run(goal)` 自动分解目标、执行计划、返回结果
- 计划阶段：LLM 将目标分解为有序步骤列表
- 执行阶段：逐一执行步骤，每步可访问目标、计划、前序结果
- 支持在步骤中委派给 AgentTool（专精 Agent）
- `run_with_log(goal)` 返回完整执行记录

**Non-Goals:**
- 不实现动态计划调整（执行中修改计划）—— v1 是静态计划
- 不实现并行步骤执行—— v1 是顺序执行
- 不实现多轮计划迭代（plan → execute → replan）—— v1 是一次计划
- 不修改现有 Agent 类

## Decisions

### Decision 1: 独立于 Agent 类

**选择**：PlanAndExecuteAgent 不继承 Agent。它是独立的类，有自己的执行模型。

**理由**：
- Agent 的核心是 ReAct 循环（Thought/Action/Observation），PlanAndExecute 是 Plan → Execute → Collect，两种模式不兼容
- 独立类的 API 可以更贴合 Plan-and-Execute 的心智模型（`run(goal)` vs `run(question)`）
- 但 PlanAndExecuteAgent 的执行步骤**可以**使用 AgentTool 委派给 Agent 实例——组合优于继承

### Decision 2: 两阶段流程（Plan 分离）

**选择**：计划阶段和执行阶段分离。先调用一次 LLM 生成完整计划，再逐一执行步骤。

**替代方案**：
- 在每步执行前动态决定下一步（类似 ReAct）：更灵活但更复杂，且失去了"计划可视化"的价值
- 计划和执行融合在一个 ReAct 循环中：其实就是当前 Agent 的行为，不算新能力

**理由**：分离的 Plan 阶段让用户能看到完整计划，也让"目标分解"成为一个可观察的中间产物。

### Decision 3: 计划格式

**选择**：LLM 输出一个编号列表，每行一个步骤。使用简单的行解析（"1. xxx", "2. xxx", ...）。

**理由**：简单可解析，不需要 JSON parser，LLM 天然输出编号列表。

### Decision 4: 步骤执行方式

**选择**：每步构建包含目标、计划、前序结果的 prompt，调用 executor LLM。如果提供了 tools 参数，executor LLM 可以在 ReAct 循环中使用给出的 tools（包括 AgentTool）。

**理由**：每步独立执行让步骤之间不互相污染，同时前序结果的 context 让后续步骤有完整的背景。

### Decision 5: API 与 Agent 保持一致

**选择**：PlanAndExecuteAgent 暴露 `run(goal)` → str 和 `run_with_log(goal)` → dict，与 Agent 的 API 对称。

**理由**：API 一致性让使用者可以互换 Agent 和 PlanAndExecuteAgent。

### Decision 6: 构造函数参数

```python
class PlanAndExecuteAgent:
    def __init__(
        self,
        llm: LLM,                         # 计划和执行共用（可以后续拆分）
        tools: Optional[List[Tool]] = None,  # 执行阶段可用的 tools
        max_steps: int = 10,               # 最多步骤数
    ):
```

**理由**：最小参数集，llm 同时用于计划和执行（简化），tools 可选（不需要工具也能用），max_steps 防止无限计划。

## Risks / Trade-offs

- **计划质量依赖 LLM**：如果 LLM 生成的计划不合理，执行结果也会差。→ 计划在 `run_with_log` 中暴露，使用者可以审查。后续可加入人工确认环节。
- **Context 膨胀**：每步执行包含所有前序结果，prompt 会越来越长。→ max_steps 限制 + LLM 上下文窗口自然上限。后续可加入计划摘要压缩。
- **静态计划不能适应新信息**：如果第 3 步发现新信息需要修改第 5 步，当前设计不做调整。→ v2 加入 replan 能力。
