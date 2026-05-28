## ADDED Requirements

### Requirement: CallbackHandler ABC interface
CallbackHandler SHALL be an abstract base class defining lifecycle hook methods that components invoke at key execution points. Each hook method SHALL accept `**kwargs` for extensibility. CallbackHandler SHALL define the following hooks: `on_llm_start`, `on_llm_end`, `on_chain_start`, `on_chain_end`, `on_tool_start`, `on_tool_end`, `on_agent_action`, `on_agent_finish`, and `on_error`.

#### Scenario: Custom handler receives lifecycle events
- **WHEN** a subclass of CallbackHandler is created with implementations for on_chain_start and on_chain_end
- **THEN** those methods are called at the appropriate execution points, receiving event-specific keyword arguments

### Requirement: StdOutCallbackHandler
StdOutCallbackHandler SHALL be a built-in CallbackHandler that prints execution events to stdout in a human-readable format. Each event SHALL be formatted as `[ComponentType] Event: detail`, e.g. `[LLMChain] Start: What is Python?`.

#### Scenario: StdOut handler prints chain execution
- **WHEN** StdOutCallbackHandler is attached to an LLMChain and `run(question="What is Python?")` is called
- **THEN** stdout shows `[LLMChain] Start: What is Python?` and `[LLMChain] End: Python is a programming language`

#### Scenario: StdOut handler prints agent reasoning steps
- **WHEN** StdOutCallbackHandler is attached to an Agent and the Agent takes an action
- **THEN** stdout shows `[Agent] Action: calculator[2+3]` and `[Tool] Start: calculator` and `[Tool] End: 5`

#### Scenario: StdOut handler prints errors
- **WHEN** StdOutCallbackHandler is attached and an LLM call raises an error
- **THEN** stdout shows `[LLM] Error: <error message>`