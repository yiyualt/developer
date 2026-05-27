## ADDED Requirements

### Requirement: Agent ReAct execution loop
Agent SHALL execute a ReAct (Reasoning + Acting) loop: in each iteration, the LLM generates a Thought and either an Action (tool call) or a Final Answer. If an Action is generated, Agent calls the corresponding Tool, receives an Observation, and appends it to the prompt for the next iteration. If a Final Answer is generated, the loop terminates. Agent SHALL also accept an optional `memory` parameter. When memory is set, `run()` SHALL load conversation history via `memory.load_context()` and include it in the initial prompt, and save the final question+answer via `memory.save_context()` after execution.

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