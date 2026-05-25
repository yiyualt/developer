## MODIFIED Requirements

### Requirement: LLMChain composition
LLMChain SHALL compose a PromptTemplate, an LLM, and an optional OutputParser. The chain SHALL declare `output_keys` — a list of key names that this chain produces. When no OutputParser is set, `output_keys` defaults to `["text"]`. When OutputParser returns a dict, `output_keys` reflects the dict's keys. This enables SequentialChain to know what each step produces.

#### Scenario: Default output_keys without parser
- **WHEN** LLMChain is created without output_parser
- **THEN** `output_keys` is `["text"]`

#### Scenario: Output_keys with JsonOutputParser
- **WHEN** LLMChain is created with JsonOutputParser
- **THEN** `output_keys` reflects the expected JSON dict keys