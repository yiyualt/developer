## ADDED Requirements

### Requirement: Tool ABC interface
Tool SHALL be an abstract base class defining three attributes: `name` (a unique string identifier), `description` (a short description for LLM tool selection), and `run(input: str) -> str` (the execution method). Tool SHALL accept an optional `callbacks` parameter (list of CallbackHandler instances). When callbacks are provided, Tool SHALL invoke `on_tool_start` before execution with the tool name and input, invoke `on_tool_end` after execution with the output, and invoke `on_error` if execution raises an exception.

#### Scenario: Tool subclass implementation
- **WHEN** a subclass of Tool is created with name="calculator", description="Useful for arithmetic", and run() that evaluates math expressions
- **THEN** the tool can be invoked via `run("2+3")` returning "5"

#### Scenario: Tool with callbacks fires lifecycle events
- **WHEN** CalculatorTool with callbacks=[handler] calls `run("2+3")` successfully
- **THEN** handler receives on_tool_start(tool_name="calculator", tool_input="2+3") and on_tool_end(output="5") in that order

#### Scenario: Tool fires on_error on execution failure
- **WHEN** a Tool with callbacks=[handler] calls `run()` and execution raises an exception
- **THEN** handler receives on_error(error=<the exception>) and on_tool_end is NOT called

### Requirement: Tool JSON Schema for function calling
Tool SHALL provide a `to_json_schema()` method returning a dict in OpenAI function calling format with `type`, `function.name`, `function.description`, and `function.parameters`. The default parameters SHALL be `{"type": "object", "properties": {"input": {"type": "string"}}}`.

#### Scenario: CalculatorTool JSON Schema
- **WHEN** CalculatorTool().to_json_schema() is called
- **THEN** the result SHALL have `type="function"` and `function.name="calculator"` and include `parameters.properties.input`

### Requirement: CalculatorTool
CalculatorTool SHALL evaluate simple arithmetic expressions provided as input string and return the result as a string.

#### Scenario: Basic arithmetic
- **WHEN** CalculatorTool.run("2+3") is called
- **THEN** it returns "5"

#### Scenario: Invalid expression
- **WHEN** CalculatorTool.run("abc") is called
- **THEN** it returns an error message string like "Error: invalid expression"

### Requirement: SearchTool (simulated)
SearchTool SHALL simulate a web search by returning pre-defined mock results for known queries and a generic response for unknown queries.

#### Scenario: Known query
- **WHEN** SearchTool.run("Python programming language") is called
- **THEN** it returns a pre-defined mock result about Python

#### Scenario: Unknown query
- **WHEN** SearchTool.run("quantum gravity") is called
- **THEN** it returns a generic mock response like "No specific results found for 'quantum gravity'"

### Requirement: PythonREPLTool
PythonREPLTool SHALL execute Python code provided as input and return the stdout output as a string. If execution fails, it SHALL return the error message.

#### Scenario: Successful execution
- **WHEN** PythonREPLTool.run("print(2+3)") is called
- **THEN** it returns "5"

#### Scenario: Execution error
- **WHEN** PythonREPLTool.run("import nonexistent") is called
- **THEN** it returns an error message string containing "ModuleNotFoundError"