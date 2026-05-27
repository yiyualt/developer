## MODIFIED Requirements

### Requirement: Agent ReAct execution loop
Agent SHALL execute a ReAct (Reasoning + Acting) loop: in each iteration, the LLM generates a Thought and either an Action (tool call) or a Final Answer. If an Action is generated, Agent calls the corresponding Tool, receives an Observation, and appends it to the prompt for the next iteration. If a Final Answer is generated, the loop terminates. Agent SHALL also accept an optional `memory` parameter. When memory is set, `run()` SHALL load conversation history via `memory.load_context()` and include it in the initial prompt, and save the final question+answer via `memory.save_context()` after execution.

#### Scenario: Agent with memory across multiple runs
- **WHEN** Agent is created with a ConversationBufferMemory, then `run(question="What is Python?")` is called and returns "Python is a programming language", then `run(question="What about its creator?")` is called
- **THEN** the second call's prompt includes the history of the first call, allowing the LLM to refer to the prior context