## MODIFIED Requirements

### Requirement: LLMChain composition
LLMChain SHALL compose a PromptTemplate, an LLM, and an optional OutputParser. The chain SHALL declare `output_keys` — a list of key names that this chain produces. When no OutputParser is set, `output_keys` defaults to `["text"]`. When OutputParser returns a dict, `output_keys` reflects the dict's keys. This enables SequentialChain to know what each step produces. LLMChain SHALL also accept an optional `memory` parameter. When memory is set, `run()` SHALL load conversation history via `memory.load_context()` before formatting the prompt, and save the current interaction via `memory.save_context()` after execution. LLMChain SHALL support arbitrary input variables in its PromptTemplate, including `{context}` for RetrievalChain integration — this is already supported by PromptTemplate's variable system and requires no code change, only documentation clarification.

#### Scenario: Chain execution with context variable
- **WHEN** LLMChain is created with a PromptTemplate containing `{context}` and `{question}` variables, then `run(context="LangChain is a framework", question="What is LangChain?")` is called
- **THEN** the prompt is formatted with both context and question, and the LLM response is returned