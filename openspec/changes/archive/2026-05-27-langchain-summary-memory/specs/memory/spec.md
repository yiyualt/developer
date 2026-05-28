## MODIFIED Requirements

### Requirement: Memory abstract interface
Memory SHALL define an ABC with three methods: `save_context(inputs, outputs)` to store one round, `load_context() -> str` to return formatted history, and `clear()` to reset stored history. ConversationSummaryMemory extends this interface by accepting an `llm` parameter and maintaining an internal `_summary` state alongside `_buffer`, enabling LLM-powered history compression.

#### Scenario: SummaryMemory is a valid Memory implementation
- **WHEN** ConversationSummaryMemory is created with an LLM instance
- **THEN** it can be used as a `memory` parameter for LLMChain and Agent, just like ConversationBufferMemory