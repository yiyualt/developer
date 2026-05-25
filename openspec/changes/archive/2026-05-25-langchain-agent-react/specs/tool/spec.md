## ADDED Requirements

### Requirement: Tool ABC interface
Tool SHALL be an abstract base class defining three attributes: `name` (a unique string identifier), `description` (a short description for LLM tool selection), and `run(input: str) -> str` (the execution method).

#### Scenario: Tool subclass implementation
- **WHEN** a subclass of Tool is created with name="calculator", description="Useful for arithmetic", and run() that evaluates math expressions
- **THEN** the tool can be invoked via `run("2+3")` returning "5"

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