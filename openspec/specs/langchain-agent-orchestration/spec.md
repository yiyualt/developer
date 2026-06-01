## ADDED Requirements

### Requirement: MultiAgentOrchestrator routes questions to specialists
MultiAgentOrchestrator SHALL accept an `llm` parameter and a `specialists` list of Agent instances. Internally it SHALL wrap each specialist in an AgentTool, create an orchestrator Agent with those tools, and delegate `run(question)` to the orchestrator Agent. The orchestrator Agent SHALL use the ReAct loop to select which specialist to call.

#### Scenario: Orchestrator routes math question to math specialist
- **WHEN** MultiAgentOrchestrator is created with specialists [math_agent, creative_agent] and `run(question="What is 42*7?")` is called
- **THEN** the orchestrator Agent selects the math specialist's AgentTool and returns the math result

#### Scenario: Orchestrator with single specialist
- **WHEN** MultiAgentOrchestrator is created with one specialist and `run(question="hello")` is called
- **THEN** the orchestrator calls that specialist and returns its result

### Requirement: SequentialAgentChain executes agents in order
SequentialAgentChain SHALL accept a list of Agent instances. When `run(question)` is called, the first Agent processes the question, the second Agent processes the first's output, and so on. The output of the last Agent SHALL be returned as the final result.

#### Scenario: Two agents in sequence
- **WHEN** SequentialAgentChain is created with [agent_a, agent_b] and `run(question="process this")` is called
- **THEN** agent_a.run("process this") is called first, then agent_b.run(agent_a_result) is called, and agent_b's output is returned

#### Scenario: Single agent in sequence
- **WHEN** SequentialAgentChain is created with one agent
- **THEN** `run(question)` returns that agent's result directly

### Requirement: Both orchestrators support run_with_log
Both MultiAgentOrchestrator and SequentialAgentChain SHALL provide a `run_with_log(question)` method that returns a dict containing the final answer and execution details.

#### Scenario: Orchestrator run_with_log
- **WHEN** `MultiAgentOrchestrator.run_with_log(question)` is called
- **THEN** the returned dict SHALL contain "final_answer" and "steps" keys with execution details

#### Scenario: SequentialAgentChain run_with_log
- **WHEN** `SequentialAgentChain.run_with_log(question)` is called
- **THEN** the returned dict SHALL contain "final_answer" and "steps" keys with each Agent's input and output
