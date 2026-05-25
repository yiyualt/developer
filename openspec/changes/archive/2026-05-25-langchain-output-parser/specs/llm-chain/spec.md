## MODIFIED Requirements

### Requirement: LLMChain composition
LLMChain SHALL compose a PromptTemplate and an LLM into a single executable unit. The chain SHALL accept an optional `output_parser` parameter. When `output_parser` is provided, `run()` and `apply()` SHALL return the parser's output instead of raw LLM response strings. When `output_parser` is not provided, behavior SHALL remain identical to v0.0.1 (returning raw strings).

#### Scenario: Chain execution with single variable (no parser)
- **WHEN** LLMChain is created with a PromptTemplate and an LLM (no output_parser), then `run(name="World")` is called
- **THEN** a raw LLM response string is returned (v0.0.1 behavior unchanged)

#### Scenario: Chain execution with JsonOutputParser
- **WHEN** LLMChain is created with a PromptTemplate, an LLM, and a JsonOutputParser, then `run(topic="Python")` is called
- **THEN** the LLM response is passed through JsonOutputParser.parse() and the parsed dict is returned

#### Scenario: Chain execution with ListOutputParser via apply
- **WHEN** LLMChain is created with an LLM and a ListOutputParser, then `apply([{"topic": "languages"}])` is called
- **THEN** each LLM response is parsed through ListOutputParser.parse() and a list of parsed lists is returned