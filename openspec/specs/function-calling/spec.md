## ADDED Requirements

### Requirement: Tool provides JSON Schema for function calling
Tool ABC SHALL provide a `to_json_schema()` method returning a dict in OpenAI function calling format with keys `type`, `function` (containing `name`, `description`, `parameters`). The default `parameters` SHALL be `{"type": "object", "properties": {"input": {"type": "string"}}}`.

#### Scenario: Default JSON Schema for CalculatorTool
- **WHEN** `CalculatorTool().to_json_schema()` is called
- **THEN** the returned dict SHALL have `type="function"` and `function.name="calculator"` and `function.parameters.properties.input.type="string"`

### Requirement: OpenAI generate_with_tools sends tools to API
OpenAI SHALL provide `generate_with_tools(messages_list, tools)` that sends tool definitions to the Chat Completions API. The return SHALL be a list of dicts with `content` and `tool_calls` keys.

#### Scenario: Model returns tool call
- **WHEN** `generate_with_tools` is called and the model decides to use a tool
- **THEN** the response SHALL contain `content=None` and `tool_calls` with `name` and `arguments`

#### Scenario: Model returns text directly
- **WHEN** `generate_with_tools` is called and the model answers without tools
- **THEN** the response SHALL contain `content="answer text"` and `tool_calls=[]`

### Requirement: FunctionCallingAgent uses native function calling
FunctionCallingAgent SHALL accept `llm`, `tools`, optional `system_message`, `memory`, `callbacks`. The ReAct loop SHALL use `generate_with_tools` instead of parsing strings. Tool calls SHALL come from the API's structured response, not regex parsing.

#### Scenario: Agent calls a tool via function calling
- **WHEN** FunctionCallingAgent with CalculatorTool runs "What is 2+3?"
- **THEN** the LLM SHALL receive a tools parameter with the calculator function definition, and SHALL return a tool_call with name="calculator"
