## ADDED Requirements

### Requirement: Agent description attribute
Agent SHALL accept an optional `description` parameter in its constructor, defaulting to an empty string. The `description` attribute SHALL be a human-readable description of the Agent's capabilities, used when the Agent is wrapped in an AgentTool to inform the orchestrator Agent about this specialist's expertise.

#### Scenario: Agent created with description
- **WHEN** Agent is created with `description="Solves complex math problems step by step"`
- **THEN** `agent.description` SHALL return "Solves complex math problems step by step"

#### Scenario: Agent created without description
- **WHEN** Agent is created without a `description` parameter
- **THEN** `agent.description` SHALL be an empty string
