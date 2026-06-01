## ADDED Requirements

### Requirement: @tool decorator converts function to Tool
The `@tool` decorator SHALL convert a function into a Tool instance. The function name SHALL become the Tool's `name` attribute. The first non-empty line of the function's docstring SHALL become the Tool's `description` attribute. The function body SHALL be called when `_run(input)` is invoked. The returned object SHALL be an instance of a Tool subclass.

#### Scenario: Basic function becomes Tool
- **WHEN** a function `def greet(name: str) -> str: """Greets a person.""" return f"Hello, {name}"` is decorated with `@tool`
- **THEN** `greet.name` SHALL be `"greet"`, `greet.description` SHALL be `"Greets a person."`, and `greet.run("World")` SHALL return `"Hello, World"`

#### Scenario: Decorated function is a Tool instance
- **WHEN** a function is decorated with `@tool`
- **THEN** `isinstance(result, Tool)` SHALL be True

#### Scenario: Decorator with explicit name and description
- **WHEN** `@tool(name="calculator", description="Performs math")` is applied to a function
- **THEN** the resulting Tool SHALL have `name="calculator"` and `description="Performs math"`

#### Scenario: Docstring with multiple lines
- **WHEN** a function has a multi-line docstring
- **THEN** only the first non-empty line SHALL be used as the Tool's description

#### Scenario: Function without docstring
- **WHEN** a function without a docstring is decorated with `@tool`
- **THEN** the Tool's description SHALL be an empty string
