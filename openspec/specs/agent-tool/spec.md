## ADDED Requirements

### Requirement: AgentTool wraps Agent as Tool
AgentTool SHALL inherit from Tool and wrap an Agent instance so that the Agent can be used as a Tool by another Agent. AgentTool SHALL implement `_run(input: str) -> str` by delegating to `agent.run(question=input)`. AgentTool SHALL have a `name` attribute (set at construction) and a `description` attribute (defaulting to the wrapped Agent's `description`, or a fallback string if neither is set). AgentTool SHALL accept an optional `callbacks` parameter and pass it to the Tool base class. When `_run` is called, AgentTool SHALL execute the wrapped Agent synchronously via `agent.run()` and return the result string. If `agent.run()` raises an exception, AgentTool SHALL catch it and return an error message string prefixed with "Agent execution error:".

#### Scenario: AgentTool delegates question to wrapped Agent
- **WHEN** an AgentTool wraps a math Agent (with CalculatorTool), and `run("What is 2+3?")` is called
- **THEN** the wrapped Agent executes its ReAct loop to answer "2+3=5", and AgentTool returns "5"

#### Scenario: AgentTool uses Agent description by default
- **WHEN** AgentTool is created with `name="math_expert"` and an Agent with `description="Solves math problems using a calculator"`
- **THEN** AgentTool.description SHALL be "Solves math problems using a calculator"

#### Scenario: AgentTool overwrites description when provided
- **WHEN** AgentTool is created with `name="math_expert"`, `description="Custom description"`, and an Agent with `description="Agent description"`
- **THEN** AgentTool.description SHALL be "Custom description"

#### Scenario: AgentTool fallback description when neither Agent nor AgentTool has one
- **WHEN** AgentTool is created with `name="math_expert"` and an Agent with `description=""`
- **THEN** AgentTool.description SHALL be "Delegates to math_expert specialist agent"

#### Scenario: AgentTool returns error on wrapped Agent failure
- **WHEN** AgentTool wraps an Agent, and `agent.run()` raises RuntimeError("LLM connection failed")
- **THEN** AgentTool._run SHALL return "Agent execution error: LLM connection failed"

#### Scenario: AgentTool IS-A Tool so works in Agent's tools list
- **WHEN** an orchestrator Agent is created with `tools=[AgentTool(name="expert", agent=specialist_agent)]`
- **THEN** the orchestrator Agent treats it like any other Tool, including it in the ReAct prompt's tool descriptions and calling it via `_execute_tool`

### Requirement: Agent description attribute
Agent SHALL accept an optional `description` parameter in its constructor, defaulting to an empty string. The `description` attribute SHALL be a human-readable description of the Agent's capabilities, used when the Agent is wrapped in an AgentTool to inform the orchestrator Agent about this specialist's expertise.

#### Scenario: Agent created with description
- **WHEN** Agent is created with `description="Solves complex math problems step by step"`
- **THEN** `agent.description` SHALL return "Solves complex math problems step by step"

#### Scenario: Agent created without description
- **WHEN** Agent is created without a `description` parameter
- **THEN** `agent.description` SHALL be an empty string
