## MODIFIED Requirements

### Requirement: LLM abstract base class
The LLM class SHALL be an abstract base class that defines the interface for all language model implementations. Subclasses MUST implement the `_generate` method. Subclasses MAY implement the `_stream` method for streaming generation; if `_stream` is not implemented, calling `stream()` SHALL raise NotImplementedError.

#### Scenario: Subclass implements _generate
- **WHEN** a class inherits from LLM and implements `_generate(prompts: list[str]) -> list[str]`
- **THEN** calling `generate(prompts)` on that instance delegates to `_generate` and returns the results

#### Scenario: Subclass does not implement _generate
- **WHEN** a class inherits from LLM without implementing `_generate`
- **THEN** instantiating that class raises TypeError

#### Scenario: Subclass implements _stream
- **WHEN** a class inherits from LLM and implements `_stream(prompt: str) -> Generator[str, None, None]`
- **THEN** calling `stream(prompt)` on that instance delegates to `_stream` and yields tokens

#### Scenario: Subclass does not implement _stream
- **WHEN** a class inherits from LLM without implementing `_stream` and `stream(prompt)` is called
- **THEN** NotImplementedError is raised

### Requirement: LLM generate method
The LLM base class SHALL provide a `generate(prompts: list[str]) -> list[str]` public method that accepts a list of prompt strings and returns a list of corresponding response strings. The LLM base class SHALL also provide a `stream(prompt: str) -> Generator[str, None, None]` public method that accepts a single prompt string and yields tokens one at a time.

#### Scenario: Generate single prompt
- **WHEN** `generate(["What is Python?"])` is called on a valid LLM subclass instance
- **THEN** a list containing one response string is returned

#### Scenario: Generate multiple prompts
- **WHEN** `generate(["What is Python?", "What is Rust?"])` is called on a valid LLM subclass instance
- **THEN** a list containing two response strings is returned

#### Scenario: Stream single prompt
- **WHEN** `stream("What is Python?")` is called on a valid LLM subclass instance that implements `_stream`
- **THEN** a generator is returned that yields tokens, and concatenating all tokens equals the full response