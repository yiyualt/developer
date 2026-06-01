## ADDED Requirements

### Requirement: OutputParser abstract base class
OutputParser SHALL be an abstract base class that defines the `parse(text: str) -> Any` interface. Subclasses MUST implement the `parse` method. OutputParser SHALL implement the Runnable interface; `invoke(input: str)` SHALL delegate to `parse(input)`.

#### Scenario: Subclass implements parse
- **WHEN** a class inherits from OutputParser and implements `parse(text: str)`
- **THEN** calling `parse("some text")` on that instance returns the parsed result

#### Scenario: Subclass does not implement parse
- **WHEN** a class inherits from OutputParser without implementing `parse`
- **THEN** instantiating that class raises TypeError

### Requirement: JsonOutputParser implementation
JsonOutputParser SHALL extract and parse JSON from LLM output text. It SHALL handle JSON embedded in markdown code blocks (```json ... ```) and raw JSON objects, returning a Python dict.

#### Scenario: Parse raw JSON
- **WHEN** `parse('{"topic": "Python", "type": "编程语言"}')` is called on JsonOutputParser
- **THEN** the result is `{"topic": "Python", "type": "编程语言"}` as a Python dict

#### Scenario: Parse JSON in markdown code block
- **WHEN** `parse('Here is the result:\n```json\n{"topic": "Python"}\n```')` is called on JsonOutputParser
- **THEN** the result is `{"topic": "Python"}` as a Python dict

#### Scenario: No JSON found in text
- **WHEN** `parse("No JSON here, just plain text")` is called on JsonOutputParser
- **THEN** a ValueError is raised indicating no JSON was found

#### Scenario: Invalid JSON found
- **WHEN** `parse('{"broken": json}')` is called on JsonOutputParser
- **THEN** a ValueError is raised indicating JSON parsing failed

### Requirement: ListOutputParser implementation
ListOutputParser SHALL parse comma-separated items from LLM output text into a Python list of strings. It SHALL strip whitespace from each item.

#### Scenario: Parse comma-separated list
- **WHEN** `parse("Python, Rust, Go")` is called on ListOutputParser
- **THEN** the result is `["Python", "Rust", "Go"]`

#### Scenario: Parse list with extra text
- **WHEN** `parse("The languages are: Python, Rust, Go")` is called on ListOutputParser
- **THEN** the result is `["Python", "Rust", "Go"]` (extracting the comma-separated portion)

#### Scenario: No comma-separated items found
- **WHEN** `parse("Just a single word")` is called on ListOutputParser
- **THEN** the result is `["Just a single word"]` (single item as a list)