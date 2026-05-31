## Context

Agent、LLMChain、Tool 各自的 `_fire()` 方法完全相同。Agent._execute_tool 和 Tool.run() 在同一个工具调用上双重 fire。后加的 7 个类完全不支持回调。

## Goals / Non-Goals

**Goals:**
- 提取 CallbackMixin：`_fire()` 只写一次
- AgentTool 继承 mixin 并传递回调给内部 Agent
- PlanAndExecuteAgent、MultiAgentOrchestrator、SequentialAgentChain、SelfCorrectingAgent、LLMCorrector：接受 callbacks 参数
- 消除 Agent._execute_tool 中的双重回调

**Non-Goals:**
- 不修改 CallbackHandler ABC
- 不修改文档（纯内部一致性重构）

## Decisions

### Decision 1: CallbackMixin — 最小 mixin

```python
class CallbackMixin:
    callbacks: List[CallbackHandler] = []
    
    def _fire(self, event, **kwargs):
        for handler in self.callbacks:
            getattr(handler, event)(**kwargs)
```

Tool、Agent、LLMChain 改继承这个 mixin。新类也继承。

### Decision 2: Agent._execute_tool 不再 fire

当前 `Agent._execute_tool` fires `on_tool_start`/`on_tool_end`/`on_error`。但 `Tool.run()` 已 fire 相同事件。直接删除 Agent 层的重复 fire，只保留 Agent 特有的 `on_agent_action`。

### Decision 3: 新类的事件映射

| 组件 | 事件 |
|------|------|
| PlanAndExecuteAgent.run | on_chain_start → per-step events → on_chain_end |
| MultiAgentOrchestrator.run | 委托给内部 Agent（Agent 自己 fire） |
| SequentialAgentChain.run | on_chain_start/end，内部 Agent 各自 fire |
| SelfCorrectingAgent.run | on_chain_start/end，内部 Agent 各自 fire |
| LLMCorrector.check | on_llm_start/end（校验调用了 LLM） |
| AgentTool._run | 委托给 Agent（Agent 自己 fire） |

AgentTool 不需要自己 fire——它包装的 Agent 已经有回调。但 AgentTool 应该能接受 callbacks 并传给 Agent。

### Decision 4: AgentTool 传递 callbacks

```python
class AgentTool(Tool):
    def __init__(self, name, agent, description="", callbacks=None):
        super().__init__(callbacks=callbacks)
        self.name = name
        self.agent = agent
        # 把 AgentTool 的 callbacks 合并到 Agent 的回调中
        if callbacks:
            self.agent.callbacks = list(set(self.agent.callbacks + callbacks))
```
