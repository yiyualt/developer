## ADDED Requirements

### Requirement: ConversationalAgent uses message-based ReAct loop
ConversationalAgent SHALL accept `llm`, `tools`, `system_message` (str), optional `memory`, optional `callbacks`. Its ReAct loop SHALL build a message list with `SystemMessage`, Memory history, a `HumanMessage` for the question, and scratchpad messages. LLM calls SHALL use `generate_messages()` with correct roles. `run(question)` SHALL return the final answer string. `run_with_log(question)` SHALL return a dict with "answer" and "log".

#### Scenario: Single-turn conversation without memory
- **WHEN** ConversationalAgent is created with system_message="You are helpful" and `run("What is 2+2?")` is called
- **THEN** the LLM SHALL receive messages including SystemMessage("You are helpful") and HumanMessage("What is 2+2?")

#### Scenario: Multi-turn conversation with memory
- **WHEN** ConversationalAgent with memory runs "hi" then "what's my name?"
- **THEN** the second call SHALL have access to the first conversation via load_messages()

#### Scenario: ReAct with tool use
- **WHEN** ConversationalAgent with CalculatorTool runs "What is 2+3?"
- **THEN** the agent SHALL use the tool and return "5"
