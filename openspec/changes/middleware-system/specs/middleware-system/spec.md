## ADDED Requirements

### Requirement: Middleware ABC defines before_tool hook
Middleware SHALL be an ABC with a `before_tool(tool_name, tool_input)` method returning `(should_proceed: bool, modified_input: str)`. Default implementation SHALL return `(True, tool_input)` — pass through unchanged.

#### Scenario: Default middleware passes through
- **WHEN** a Middleware subclass with no override receives `before_tool("calc", "2+3")`
- **THEN** it SHALL return `(True, "2+3")`

### Requirement: HumanInTheLoopMiddleware implements interrupt_on
HumanInTheLoopMiddleware SHALL accept `interrupt_on` (dict mapping tool names to True/False/config dict) and optional `approver` callable. `before_tool` SHALL check if the tool is in `interrupt_on` with a truthy value; if so, call the approver.

#### Scenario: Tool in interrupt_on triggers approver
- **WHEN** HITL middleware has `interrupt_on={"send_email": True}` and `before_tool("send_email", "body")` is called
- **THEN** the approver SHALL be called

#### Scenario: Tool not in interrupt_on passes through
- **WHEN** HITL middleware has `interrupt_on={"send_email": True}` and `before_tool("calculator", "2+3")` is called
- **THEN** it SHALL return `(True, "2+3")` without calling the approver

### Requirement: Agent accepts middleware list
Agent SHALL accept `middleware: Optional[List[Middleware]]` parameter. `_execute_tool` SHALL iterate all middleware calling `before_tool` before tool execution. If any middleware returns `(False, _)`, the tool SHALL be skipped.

#### Scenario: Multiple middleware in pipeline
- **WHEN** Agent has `middleware=[AuditMiddleware(), HumanInTheLoopMiddleware()]` and a tool is called
- **THEN** both middleware's `before_tool` SHALL be called in order

### Requirement: Tool requires_approval is removed
Tool ABC SHALL no longer have a `requires_approval` attribute. Approval configuration lives entirely in middleware.

#### Scenario: Tool has no requires_approval
- **WHEN** CalculatorTool is inspected
- **THEN** it SHALL NOT have a `requires_approval` attribute
