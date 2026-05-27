## MODIFIED Requirements

### Requirement: LLMChain composition
LLMChain SHALL compose a PromptTemplate, an LLM, and an optional OutputParser. The chain SHALL declare `output_keys` — a list of key names that this chain produces. When no OutputParser is set, `output_keys` defaults to `["text"]`. When OutputParser returns a dict, `output_keys` reflects the dict's keys. This enables SequentialChain to know what each step produces. LLMChain SHALL also accept an optional `memory` parameter. When memory is set, `run()` SHALL load conversation history via `memory.load_context()` before formatting the prompt, and save the current interaction via `memory.save_context()` after execution.

#### Scenario: LLMChain with memory
- **WHEN** LLMChain is created with a ConversationBufferMemory, then `run(question="What is Python?")` is called
- **THEN** the memory's conversation history is prepended to the prompt, the LLM generates a response, and the interaction (input and output) is saved to memory via `save_context()`

#### Scenario: LLMChain without memory (existing behavior)
- **WHEN** LLMChain is created without memory
- **THEN** `run()` and `apply()` behave exactly as before — no history is loaded or saved