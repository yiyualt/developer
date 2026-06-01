## ADDED Requirements

### Requirement: Middleware ABC defines before_llm hook
Middleware ABC SHALL define `before_llm(messages) -> messages` that returns the message list unchanged by default. Subclasses MAY override this to transform messages before each LLM call.

#### Scenario: Default before_llm passes through
- **WHEN** a Middleware with no override receives before_llm([msg1, msg2])
- **THEN** it SHALL return [msg1, msg2] unchanged

### Requirement: Agent calls before_llm in the ReAct loop
Agent's ReAct loop SHALL call `mw.before_llm(call_messages)` for each registered middleware before every LLM call. The returned message list SHALL be used for the LLM call.

### Requirement: SummarizationMiddleware compresses old messages
SummarizationMiddleware SHALL accept `llm`, optional `max_tokens` and `keep_recent`. `before_llm` SHALL check total message character count against `max_tokens * 4`. If over threshold, older messages SHALL be summarized via LLM into a single HumanMessage, keeping the most recent `keep_recent` messages unchanged.

#### Scenario: Messages under threshold — no summarization
- **WHEN** messages total < max_tokens*4 characters
- **THEN** before_llm SHALL return the messages unchanged

#### Scenario: Messages over threshold — older messages replaced with summary
- **WHEN** messages exceed the character threshold
- **THEN** before_llm SHALL return a list starting with a summary HumanMessage, followed by the latest keep_recent messages
