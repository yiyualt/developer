## ADDED Requirements

### Requirement: Agent ReAct execution loop
Agent SHALL execute a ReAct (Reasoning + Acting) loop: in each iteration, the LLM generates a Thought and either an Action (tool call) or a Final Answer. If an Action is generated, Agent calls the corresponding Tool, receives an Observation, and appends it to the prompt for the next iteration. If a Final Answer is generated, the loop terminates. Agent SHALL also accept an optional `memory` parameter. When memory is set, `run()` SHALL load conversation history via `memory.load_context()` and include it in the initial prompt. When the loop finishes, Agent SHALL save the complete ReAct reasoning process to memory via `memory.save_context()` — including the Thought, Actions, Observations, and Final Answer, not just the Final Answer alone. Agent SHALL accept an optional `callbacks` parameter (list of CallbackHandler instances). When callbacks are provided, Agent SHALL invoke `on_agent_action` when a tool action is selected, invoke `on_tool_start` before calling the tool, invoke `on_tool_end` after receiving the tool result, invoke `on_agent_finish` when a Final Answer is produced, and invoke `on_error` if any step raises an exception. Agent SHALL accept an optional `approver` parameter (Callable[[str, str], tuple]). When a tool has `requires_approval=True` and an approver is set, Agent SHALL call the approver before executing the tool; if `(False, _)` is returned, the tool is skipped; if `(True, modified_input)`, execution proceeds with the modified input.

#### Scenario: Agent saves full reasoning to memory
- **WHEN** Agent with memory runs and produces Thought="I should search", Action="search[Paris population]", Observation="2.2 million", Final Answer="Paris has about 2.2 million people"
- **THEN** `memory.save_context()` is called with outputs containing the full reasoning: "Thought: I should search\nAction: search[Paris population]\nObservation: 2.2 million\nFinal Answer: Paris has about 2.2 million people"

#### Scenario: Agent with callbacks fires reasoning events
- **WHEN** Agent with callbacks=[handler] runs and produces Thought="I should calculate", Action="calculator[2+3]", Observation="5", Final Answer="5"
- **THEN** handler receives on_agent_action(action="calculator[2+3]"), on_tool_start(tool_name="calculator", tool_input="2+3"), on_tool_end(output="5"), on_agent_finish(final_answer="5") in that order

#### Scenario: Agent resolves question using a tool
- **WHEN** Agent is created with an LLM and a Calculator tool, then `run(question="What is 2 + 3?")` is called
- **THEN** the LLM generates a Thought and Action `calculator[2+3]`, Agent calls CalculatorTool.run("2+3") which returns "5", the Observation "5" is appended, and the LLM generates Final Answer "5" in the next iteration

#### Scenario: Agent gives direct answer without tool
- **WHEN** Agent is created with tools, then `run(question="What color is the sky?")` is called, and the LLM determines no tool is needed
- **THEN** the LLM generates a Final Answer directly without any Action, and the loop terminates after one iteration

#### Scenario: Agent reaches max iterations
- **WHEN** Agent runs with max_iterations=3 and the LLM does not produce a Final Answer within 3 iterations
- **THEN** the loop terminates and returns the most recent Thought as the answer

### Requirement: Agent output parsing
Agent SHALL use an AgentOutputParser to extract Thought, Action, and Final Answer from each LLM response. The parser SHALL support the format `Thought: ... Action: tool_name[input]` and `Thought: ... Final Answer: ...`.

#### Scenario: Parse Thought + Action
- **WHEN** LLM response is "Thought: I should calculate this. Action: calculator[2+3]"
- **THEN** parser extracts thought="I should calculate this", action_tool="calculator", action_input="2+3"

#### Scenario: Parse Thought + Final Answer
- **WHEN** LLM response is "Thought: I now know the answer. Final Answer: The result is 5"
- **THEN** parser extracts thought="I now know the answer", final_answer="The result is 5"

#### Scenario: Parse fallback on malformed output
- **WHEN** LLM response does not contain "Action:" or "Final Answer:" markers
- **THEN** parser treats the entire response as a Thought and the loop continues without tool invocation

### Requirement: Agent execution logging
Agent SHALL provide a `run_with_log()` method that returns a dict containing the final answer and the complete execution log (list of Thought/Action/Observation entries from each iteration).

#### Scenario: Retrieve execution log
- **WHEN** `run_with_log(question="What is 2+3?")` is called and the Agent completes 2 iterations
- **THEN** the returned dict contains {"answer": "5", "log": [{"thought": "...", "action": "calculator[2+3]", "observation": "5"}, {"thought": "...", "final_answer": "5"}]}

### Requirement: Agent description attribute
Agent SHALL accept an optional `description` parameter in its constructor, defaulting to an empty string. The `description` attribute SHALL be a human-readable description of the Agent's capabilities, used when the Agent is wrapped in an AgentTool to inform the orchestrator Agent about this specialist's expertise.

#### Scenario: Agent created with description
- **WHEN** Agent is created with `description="Solves complex math problems step by step"`
- **THEN** `agent.description` SHALL return "Solves complex math problems step by step"

#### Scenario: Agent created without description
- **WHEN** Agent is created without a `description` parameter
- **THEN** `agent.description` SHALL be an empty string