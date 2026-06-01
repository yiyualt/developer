## ADDED Requirements

### Requirement: LLMChain composition
LLMChain SHALL compose a PromptTemplate, an LLM, and an optional OutputParser. The chain SHALL declare `output_keys` — a list of key names that this chain produces. When no OutputParser is set, `output_keys` defaults to `["text"]`. When OutputParser returns a dict, `output_keys` reflects the dict's keys. This enables SequentialChain to know what each step produces. LLMChain SHALL also accept an optional `memory` parameter. When memory is set, `run()` SHALL load conversation history via `memory.load_context()` before formatting the prompt, and save the current interaction via `memory.save_context()` after execution. LLMChain SHALL accept an optional `callbacks` parameter (list of CallbackHandler instances). When callbacks are provided, LLMChain SHALL invoke `on_chain_start` before execution with the input kwargs, invoke `on_llm_start` before the LLM call with the formatted prompt, invoke `on_llm_end` after the LLM call with the response, invoke `on_chain_end` after execution with the output, and invoke `on_error` if any step raises an exception. LLMChain SHALL support arbitrary input variables in its PromptTemplate, including `{context}` for RetrievalChain integration — this is already supported by PromptTemplate's variable system and requires no code change, only documentation clarification.

#### Scenario: Chain execution with single variable (no parser)
- **WHEN** LLMChain is created with a PromptTemplate and an LLM (no output_parser), then `run(name="World")` is called
- **THEN** a raw LLM response string is returned (v0.0.1 behavior unchanged)

#### Scenario: Chain execution with JsonOutputParser
- **WHEN** LLMChain is created with a PromptTemplate, an LLM, and a JsonOutputParser, then `run(topic="Python")` is called
- **THEN** the LLM response is passed through JsonOutputParser.parse() and the parsed dict is returned

#### Scenario: Chain execution with ListOutputParser via apply
- **WHEN** LLMChain is created with an LLM and a ListOutputParser, then `apply([{"topic": "languages"}])` is called
- **THEN** each LLM response is parsed through ListOutputParser.parse() and a list of parsed lists is returned

#### Scenario: Chain execution with context variable
- **WHEN** LLMChain is created with a PromptTemplate containing `{context}` and `{question}` variables, then `run(context="LangChain is a framework", question="What is LangChain?")` is called
- **THEN** the prompt is formatted with both context and question, and the LLM response is returned

#### Scenario: LLMChain with callbacks fires lifecycle events
- **WHEN** LLMChain is created with callbacks=[handler] and `run(question="What is Python?")` is called successfully
- **THEN** handler receives on_chain_start(serialized_input={"question": "What is Python?"}), on_llm_start(prompt="...formatted prompt..."), on_llm_end(response="Python is..."), on_chain_end(output="Python is...") in that order

#### Scenario: LLMChain fires on_error on LLM failure
- **WHEN** LLMChain with callbacks=[handler] calls `run()` and the LLM raises an exception
- **THEN** handler receives on_error(error=<the exception>) and on_chain_end is NOT called

### Requirement: LLMChain apply_async method
LLMChain SHALL provide an `apply_async(input_list: list[dict]) -> list[Any]` async method that concurrently processes a list of input dictionaries through the chain using the LLM's agenerate method. When output_parser is set, each LLM response is parsed before returning. Results SHALL be returned in the same order as the input list.

#### Scenario: Async apply with multiple inputs (no parser)
- **WHEN** `apply_async([{"question": "q1"}, {"question": "q2"}])` is called on an LLMChain without output_parser
- **THEN** two response strings are returned concurrently in order

#### Scenario: Async apply with output parser
- **WHEN** `apply_async([{"topic": "Python"}])` is called on an LLMChain with JsonOutputParser
- **THEN** the LLM response is parsed through JsonOutputParser.parse() concurrently and a list of parsed dicts is returned

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