## ADDED Requirements

### Requirement: ModelCallLimitMiddleware caps LLM calls
ModelCallLimitMiddleware SHALL extend Middleware and track LLM call count in `before_llm`. When `max_calls` is exceeded, `before_llm` SHALL return a single HumanMessage indicating the limit was reached.

#### Scenario: Under limit — pass through
- **WHEN** ModelCallLimitMiddleware(max_calls=3) has counted 2 calls
- **THEN** before_llm SHALL return the input messages unchanged

#### Scenario: Over limit — block
- **WHEN** ModelCallLimitMiddleware(max_calls=3) has counted 4 calls
- **THEN** before_llm SHALL return a list with a single "limit exceeded" message

### Requirement: ToolCallLimitMiddleware caps tool calls
ToolCallLimitMiddleware SHALL extend Middleware and track tool call counts in `before_tool`. It SHALL support both a global `max_calls` limit and per-tool limits via `per_tool` dict. When a limit is exceeded, `before_tool` SHALL return `(False, reason_string)`.

#### Scenario: Per-tool limit exceeded
- **WHEN** ToolCallLimitMiddleware(per_tool={"calculator": 1}) and calculator has been called twice
- **THEN** before_tool("calculator", ...) SHALL return (False, "Tool 'calculator' limit exceeded.")

#### Scenario: Tool not in per_tool — no limit
- **WHEN** ToolCallLimitMiddleware(per_tool={"calculator": 1}) and "search" is called
- **THEN** before_tool("search", ...) SHALL return (True, unchanged_input)
