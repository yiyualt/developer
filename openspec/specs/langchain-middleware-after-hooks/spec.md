## ADDED Requirements

### Requirement: Middleware ABC defines after_llm hook
Middleware ABC SHALL define `after_llm(messages, response) -> response` that returns the response unchanged by default. Subclasses MAY override to transform or replace the LLM response.

#### Scenario: Default after_llm passes through
- **WHEN** a Middleware with no override receives after_llm([msg], "response")
- **THEN** it SHALL return "response" unchanged

### Requirement: Middleware ABC defines after_tool hook
Middleware ABC SHALL define `after_tool(tool_name, tool_input, result) -> result` that returns the result unchanged by default.

#### Scenario: Default after_tool passes through
- **WHEN** a Middleware with no override receives after_tool("calc", "2+3", "5")
- **THEN** it SHALL return "5" unchanged

### Requirement: Agent calls after_llm and after_tool
Agent._react_loop SHALL call `mw.after_llm(messages, response)` for each middleware after every LLM call. Agent._execute_tool SHALL call `mw.after_tool(tool_name, tool_input, result)` after every tool execution.

#### Scenario: after_llm is called in the loop
- **WHEN** Agent runs with a middleware that overrides after_llm
- **THEN** the middleware's after_llm SHALL be called after each LLM.generate() call
