## ADDED Requirements

### Requirement: LLM stream method
LLMChain SHALL provide a `stream(**kwargs) -> Generator[str, None, None]` method that executes the chain in streaming mode. When callbacks are provided, `on_llm_new_token` SHALL be invoked for each token yielded by the LLM. The generator SHALL yield each token as a string, and the full response SHALL be available by concatenating all yielded tokens.

#### Scenario: Stream chain execution with callbacks
- **WHEN** LLMChain with callbacks=[handler] calls `stream(question="What is Python?")` and iterates over the generator
- **THEN** handler receives on_chain_start, then on_llm_start, then on_llm_new_token for each token, then on_llm_end, then on_chain_end, and each yielded token is part of the complete response

#### Scenario: Stream chain execution without callbacks
- **WHEN** LLMChain without callbacks calls `stream(question="What is Python?")` and concatenates all yielded tokens
- **THEN** the concatenated result equals the result that `run(question="What is Python?")` would return

### Requirement: Agent stream method
Agent SHALL provide a `stream(question) -> Generator[dict, None, None]` method that executes the ReAct loop in streaming mode. The generator SHALL yield step events as dicts with `type` and `content` fields. Event types SHALL be: `thought`, `action`, `observation`, `final_answer`. When callbacks are provided, `on_agent_action`, `on_tool_start`, `on_tool_end`, and `on_agent_finish` SHALL be invoked at the corresponding steps.

#### Scenario: Stream agent execution with tool use
- **WHEN** Agent with callbacks=[handler] calls `stream(question="What is 2 + 3?")` and the agent produces Thought, Action=calculator[2+3], Observation=5, Final Answer=5
- **THEN** the generator yields {"type": "thought", "content": "..."}, {"type": "action", "content": "calculator[2+3]"}, {"type": "observation", "content": "5"}, {"type": "final_answer", "content": "5"}, and handler receives on_agent_action, on_tool_start, on_tool_end, on_agent_finish

#### Scenario: Stream agent with direct answer
- **WHEN** Agent calls `stream(question="What color is the sky?")` and the LLM produces a Final Answer directly
- **THEN** the generator yields {"type": "thought", "content": "..."} and {"type": "final_answer", "content": "blue"}