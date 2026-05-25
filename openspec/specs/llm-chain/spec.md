## ADDED Requirements

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

### Requirement: LLMChain run method
LLMChain SHALL provide a `run(**kwargs) -> Any` method that accepts input variables as keyword arguments and returns a single response. When no output_parser is set, returns a string. When output_parser is set, returns the parsed result.

#### Scenario: Run returns string (no parser)
- **WHEN** `run(question="What is AI?")` is called on a LLMChain without output_parser
- **THEN** a single string (the LLM's response) is returned

#### Scenario: Run returns parsed result (with parser)
- **WHEN** `run(question="What is AI?")` is called on a LLMChain with JsonOutputParser
- **THEN** a parsed dict (the parser's output) is returned

### Requirement: LLMChain apply method
LLMChain SHALL provide an `apply(input_list: list[dict]) -> list[Any]` method that accepts a list of input dictionaries and returns a list of results, processing each input through the chain. When no output_parser is set, returns list[str]. When output_parser is set, returns list of parsed results.

#### Scenario: Apply with multiple inputs (no parser)
- **WHEN** `apply([{"name": "Alice"}, {"name": "Bob"}])` is called on a LLMChain without output_parser
- **THEN** two response strings are returned