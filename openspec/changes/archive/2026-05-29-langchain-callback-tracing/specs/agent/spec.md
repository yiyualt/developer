## MODIFIED Requirements

### Requirement: Agent ReAct execution loop
Agent SHALL execute a ReAct (Reasoning + Acting) loop: in each iteration, the LLM generates a Thought and either an Action (tool call) or a Final Answer. If an Action is generated, Agent calls the corresponding Tool, receives an Observation, and appends it to the prompt for the next iteration. If a Final Answer is generated, the loop terminates. Agent SHALL also accept an optional `memory` parameter. When memory is set, `run()` SHALL load conversation history via `memory.load_context()` and include it in the initial prompt. When the loop finishes, Agent SHALL save the complete ReAct reasoning process to memory via `memory.save_context()` — including the Thought, Actions, Observations, and Final Answer, not just the Final Answer alone. Agent SHALL accept an optional `callbacks` parameter (list of CallbackHandler instances). When callbacks are provided, Agent SHALL invoke `on_agent_action` when a tool action is selected, invoke `on_tool_start` before calling the tool, invoke `on_tool_end` after receiving the tool result, invoke `on_agent_finish` when a Final Answer is produced, and invoke `on_error` if any step raises an exception.

#### Scenario: Agent with callbacks fires reasoning events
- **WHEN** Agent with callbacks=[handler] runs and produces Thought="I should calculate", Action="calculator[2+3]", Observation="5", Final Answer="5"
- **THEN** handler receives on_agent_action(action="calculator[2+3]"), on_tool_start(tool_name="calculator", tool_input="2+3"), on_tool_end(output="5"), on_agent_finish(final_answer="5") in that order

#### Scenario: Agent saves full reasoning to memory
- **WHEN** Agent with memory runs and produces Thought="I should search", Action="search[Paris population]", Observation="2.2 million", Final Answer="Paris has about 2.2 million people"
- **THEN** `memory.save_context()` is called with outputs containing the full reasoning: "Thought: I should search\nAction: search[Paris population]\nObservation: 2.2 million\nFinal Answer: Paris has about 2.2 million people"

#### Scenario: Agent resolves question using a tool
- **WHEN** Agent is created with an LLM and a Calculator tool, then `run(question="What is 2 + 3?")` is called
- **THEN** the LLM generates a Thought and Action `calculator[2+3]`, Agent calls CalculatorTool.run("2+3") which returns "5", the Observation "5" is appended, and the LLM generates Final Answer "5" in the next iteration

#### Scenario: Agent gives direct answer without tool
- **WHEN** Agent is created with tools, then `run(question="What color is the sky?")` is called, and the LLM determines no tool is needed
- **THEN** the LLM generates a Final Answer directly without any Action, and the loop terminates after one iteration

#### Scenario: Agent reaches max iterations
- **WHEN** Agent runs with max_iterations=3 and the LLM does not produce a Final Answer within 3 iterations
- **THEN** the loop terminates and returns the most recent Thought as the answer