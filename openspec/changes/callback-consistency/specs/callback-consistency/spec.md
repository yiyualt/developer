## ADDED Requirements

### Requirement: CallbackMixin provides shared _fire implementation
CallbackMixin SHALL be a class providing `_fire(event: str, **kwargs)` that iterates `self.callbacks` and calls the matching method on each handler. Classes that need callback support SHALL inherit CallbackMixin instead of duplicating `_fire`.

#### Scenario: CallbackMixin fires event on all handlers
- **WHEN** a class inherits CallbackMixin with `callbacks=[handler1, handler2]` and calls `_fire("on_llm_start", prompt="hello")`
- **THEN** `handler1.on_llm_start(prompt="hello")` and `handler2.on_llm_start(prompt="hello")` SHALL both be called

### Requirement: New agent components accept callbacks
PlanAndExecuteAgent, MultiAgentOrchestrator, SequentialAgentChain, SelfCorrectingAgent, and LLMCorrector SHALL all accept an optional `callbacks` parameter (list of CallbackHandler instances) in their constructors, defaulting to an empty list.

#### Scenario: PlanAndExecuteAgent fires events
- **WHEN** PlanAndExecuteAgent is created with callbacks=[handler] and `run(goal)` is called
- **THEN** handler SHALL receive execution lifecycle events

#### Scenario: SelfCorrectingAgent fires events
- **WHEN** SelfCorrectingAgent is created with callbacks=[handler] and `run(question)` is called
- **THEN** handler SHALL receive events from both the corrector and the wrapped agent

### Requirement: Agent._execute_tool does not duplicate tool callbacks
Agent._execute_tool SHALL NOT call `_fire("on_tool_start")` or `_fire("on_tool_end")`. These events SHALL be fired exclusively by Tool.run(). Agent SHALL continue to fire `on_agent_action` before calling the tool.

#### Scenario: Tool events fire once per invocation
- **WHEN** Agent runs and calls a tool via `_execute_tool`
- **THEN** on_tool_start and on_tool_end SHALL each fire exactly once (from Tool.run(), not from Agent)
