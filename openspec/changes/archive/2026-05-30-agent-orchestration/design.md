## Context

AgentTool 提供了 Agent→Tool 的适配，但编排代码仍是手工的。用户需要：1) 为每个专精 Agent 创建 AgentTool；2) 构造编排 Agent；3) 管理 tools 列表。两个最常见的编排模式值得封装：路由分发（Orchestrator）和串联管道（Sequential）。

## Goals / Non-Goals

**Goals:**
- `MultiAgentOrchestrator`: 自动封装 Agent→AgentTool→编排 Agent，用户只需传入 specialists 列表
- `SequentialAgentChain`: 按顺序执行 Agent，A→B→C，前一个输出是后一个的输入

**Non-Goals:**
- 不实现并行执行模式（后续版本）
- 不实现条件分支模式（后续版本）
- 不修改 Agent 或 AgentTool

## Decisions

### Decision 1: 两个模式是两个独立类

**选择**：`MultiAgentOrchestrator` 和 `SequentialAgentChain` 是两个独立类，各有自己的 `run()` 方法。

**理由**：两种模式的语义完全不同——一个是"选择一个专家"，一个是"所有专家依次处理"。强行统一到一个抽象下反而增加理解成本。

### Decision 2: MultiAgentOrchestrator 内部用 AgentTool

```python
class MultiAgentOrchestrator:
    def __init__(self, llm, specialists, max_iterations=5):
        self.tools = [
            AgentTool(name=f"specialist_{i}", agent=a)
            for i, a in enumerate(specialists)
        ]
        self._orchestrator = Agent(llm=llm, tools=self.tools, ...)
    
    def run(self, question):
        return self._orchestrator.run(question=question)
```

AgentTool 的 name 使用 `agent.description`（如果有的话）或回退到索引名。

### Decision 3: SequentialAgentChain 每步独立调用

```python
class SequentialAgentChain:
    def __init__(self, agents):
        self.agents = agents
    
    def run(self, question):
        result = question
        for agent in self.agents:
            result = agent.run(question=result)
        return result
```

简单直接。每个 Agent 的 `run()` 是完整独立的调用（含 ReAct 循环、工具使用等）。

### Decision 4: API 与 Agent 一致

两个模式都暴露 `run(question)` → str 和 `run_with_log(question)` → dict，与 Agent API 对称。

## Risks / Trade-offs

- **Orchestrator 的 AgentTool 命名**：使用 agent.description 作为 AgentTool name，如果 description 不好会影响路由质量。→ 用户可在 Agent 构造时设好 description。
- **SequentialAgentChain 中间结果丢失**：只返回最后一个 Agent 的输出。→ `run_with_log()` 返回每步的完整记录。
