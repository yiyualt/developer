## ADDED Requirements

### Requirement: PlanAndExecuteAgent decomposes goals into plans
PlanAndExecuteAgent SHALL accept a goal string via `run(goal)` and execute a two-phase process: first decompose the goal into an ordered plan (a list of step descriptions), then execute each step sequentially. PlanAndExecuteAgent SHALL accept an `llm` parameter (LLM instance for both planning and execution) and an optional `tools` parameter (list of Tool instances available during execution, including AgentTool). The planning phase SHALL call the LLM to generate a numbered list of steps. Each step description SHALL be extracted by parsing lines that start with a number followed by a period or parenthesis.

#### Scenario: Decompose simple goal into plan
- **WHEN** `run(goal="Write a 2-sentence introduction to Python")` is called with a FakeLLM that returns "1. Research Python's key features\n2. Write the first sentence\n3. Write the second sentence\nFinal Plan" as the plan response, then "Python is a versatile language." for step 1, "It is used for web, data, and AI." for step 2, "Python is a versatile language. It is used for web, data, and AI." for step 3
- **THEN** the plan SHALL contain exactly ["Research Python's key features", "Write the first sentence", "Write the second sentence"] and the final answer SHALL combine the execution results

#### Scenario: Parse plan from LLM with various numbering formats
- **WHEN** LLM returns a plan with "1) Step A\n2) Step B\n3. Step C"
- **THEN** the parsed plan SHALL be ["Step A", "Step B", "Step C"]

### Requirement: PlanAndExecuteAgent executes steps with context
During the execution phase, PlanAndExecuteAgent SHALL execute each step in order. For each step, the execution prompt SHALL include the original goal, the full plan, all previously executed steps and their results, and the current step to execute. If `tools` are provided, the executor SHALL have access to them during step execution.

#### Scenario: Step execution passes context between steps
- **WHEN** executing step 2 of a plan, after step 1 returned "Python was created in 1991"
- **THEN** the prompt for step 2 SHALL contain both "Python was created in 1991" and the description of step 2

#### Scenario: Executor uses tools during step execution
- **WHEN** PlanAndExecuteAgent is created with tools=[CalculatorTool()] and step 1 is "Calculate 42*7"
- **THEN** the executor SHALL be able to use the CalculatorTool to compute the result for that step

### Requirement: PlanAndExecuteAgent returns final answer
`run(goal)` SHALL return a string containing the synthesized final answer after all steps are executed. `run_with_log(goal)` SHALL return a dict with keys `plan` (list of step strings), `steps` (list of dicts with `step` and `result` keys), and `final_answer` (the final synthesized result string).

#### Scenario: run returns string final answer
- **WHEN** `run(goal="Count to 2")` is called and the plan has steps ["Say 1", "Say 2"]
- **THEN** the return value SHALL be a string

#### Scenario: run_with_log returns full execution record
- **WHEN** `run_with_log(goal="Count to 2")` is called and the plan has 2 steps
- **THEN** the returned dict SHALL contain keys "plan" (list of 2 strings), "steps" (list of 2 dicts), and "final_answer" (string)

### Requirement: PlanAndExecuteAgent enforces max_steps limit
PlanAndExecuteAgent SHALL accept an optional `max_steps` parameter (default 10). If the planner generates more than `max_steps` steps, only the first `max_steps` steps SHALL be executed.

#### Scenario: Plan exceeds max_steps
- **WHEN** PlanAndExecuteAgent is created with `max_steps=3` and the planner generates a plan with 5 steps
- **THEN** only the first 3 steps SHALL be executed
