## ADDED Requirements

### Requirement: LLM abstract base class
The LLM class SHALL be an abstract base class that defines the interface for all language model implementations. Subclasses MUST implement the `_generate` method.

#### Scenario: Subclass implements _generate
- **WHEN** a class inherits from LLM and implements `_generate(prompts: list[str]) -> list[str]`
- **THEN** calling `generate(prompts)` on that instance delegates to `_generate` and returns the results

#### Scenario: Subclass does not implement _generate
- **WHEN** a class inherits from LLM without implementing `_generate`
- **THEN** instantiating that class raises TypeError

### Requirement: LLM generate method
The LLM base class SHALL provide a `generate(prompts: list[str]) -> list[str]` public method that accepts a list of prompt strings and returns a list of corresponding response strings.

#### Scenario: Generate single prompt
- **WHEN** `generate(["What is Python?"])` is called on a valid LLM subclass instance
- **THEN** a list containing one response string is returned

#### Scenario: Generate multiple prompts
- **WHEN** `generate(["What is Python?", "What is Rust?"])` is called on a valid LLM subclass instance
- **THEN** a list containing two response strings is returned

### Requirement: FakeLLM implementation
FakeLLM SHALL be a concrete LLM subclass that returns predictable responses for testing. It SHALL accept an optional `responses` dict mapping prompt strings to response strings, and return a default response for prompts not in the dict.

#### Scenario: FakeLLM with mapped response
- **WHEN** FakeLLM is created with `responses={"What is Python?": "Python is a programming language"}` and `generate(["What is Python?"])` is called
- **THEN** the result is `["Python is a programming language"]`

#### Scenario: FakeLLM with unmapped prompt
- **WHEN** FakeLLM is created with default response `"Fake response"` and `generate(["Random question"])` is called
- **THEN** the result is `["Fake response"]`

#### Scenario: FakeLLM default response
- **WHEN** FakeLLM is created without any responses argument and `generate(["Any prompt"])` is called
- **THEN** the result is `["Fake LLM response"]`