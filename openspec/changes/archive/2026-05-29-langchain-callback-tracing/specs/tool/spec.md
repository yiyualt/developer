## MODIFIED Requirements

### Requirement: Tool execution interface
Tool SHALL be an abstract base class with `name`, `description` properties and a `run(input: str) -> str` method. Tool SHALL accept an optional `callbacks` parameter (list of CallbackHandler instances). When callbacks are provided, Tool SHALL invoke `on_tool_start` before execution with the tool name and input, invoke `on_tool_end` after execution with the output, and invoke `on_error` if execution raises an exception.

#### Scenario: Tool with callbacks fires lifecycle events
- **WHEN** CalculatorTool with callbacks=[handler] calls `run("2+3")` successfully
- **THEN** handler receives on_tool_start(tool_name="calculator", tool_input="2+3") and on_tool_end(output="5") in that order

#### Scenario: Tool fires on_error on execution failure
- **WHEN** a Tool with callbacks=[handler] calls `run()` and execution raises an exception
- **THEN** handler receives on_error(error=<the exception>) and on_tool_end is NOT called