## MODIFIED Requirements

### Requirement: CallbackHandler ABC interface
CallbackHandler SHALL be an abstract base class defining lifecycle hook methods that components invoke at key execution points. Each hook method SHALL accept `**kwargs` for extensibility. CallbackHandler SHALL define the following hooks: `on_llm_start`, `on_llm_end`, `on_chain_start`, `on_chain_end`, `on_tool_start`, `on_tool_end`, `on_agent_action`, `on_agent_finish`, `on_llm_new_token`, and `on_error`.

#### Scenario: Custom handler receives lifecycle events
- **WHEN** a subclass of CallbackHandler is created with implementations for on_chain_start and on_chain_end
- **THEN** those methods are called at the appropriate execution points, receiving event-specific keyword arguments

#### Scenario: Handler receives token stream
- **WHEN** a CallbackHandler subclass implements on_llm_new_token and streaming is enabled
- **THEN** on_llm_new_token is invoked for each token yielded by the LLM, receiving `token` and `run_id` keyword arguments