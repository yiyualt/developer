## ADDED Requirements

### Requirement: Agent.apply_async runs multiple questions concurrently
Agent SHALL provide an `apply_async(questions: list[str]) -> list[str]` async method. Each question SHALL be processed in a separate ReAct loop using `llm.agenerate()` for LLM calls. Results SHALL be returned in the same order as input questions. The implementation SHALL use `asyncio.gather` for concurrency.

#### Scenario: Two questions run concurrently
- **WHEN** `await agent.apply_async(["What is 2+2?", "What is 3+3?"])` is called with a FakeLLM supporting agenerate
- **THEN** the result SHALL be `["4", "6"]` in the same order as input

#### Scenario: Single question still works
- **WHEN** `await agent.apply_async(["What is 2+2?"])` is called
- **THEN** the result SHALL be `["4"]`

#### Scenario: ReAct loop uses agenerate internally
- **WHEN** Agent.apply_async processes a question that requires tool use
- **THEN** each LLM call in the ReAct loop SHALL use `await llm.agenerate()` instead of `llm.generate()`
