## ADDED Requirements

### Requirement: SequentialChain multi-step execution
SequentialChain SHALL execute multiple LLMChains in sequence, passing each step's output as input to the next step. It SHALL accept a list of chains and an `input_variables` declaration.

#### Scenario: Two-step sequential chain
- **WHEN** SequentialChain is created with chain A (outputs {"topic": "Python"}) and chain B (takes {topic} as input), then `run(subject="Python")` is called
- **THEN** chain A executes first, its output {"topic": "Python"} is merged into chain B's input, chain B executes, and the combined output dict is returned

#### Scenario: Three-step sequential chain
- **WHEN** SequentialChain is created with three chains where each step's output feeds the next, then `run()` is called
- **THEN** all three chains execute in order, each receiving the accumulated inputs from all prior steps

### Requirement: SequentialChain returns accumulated output dict
SequentialChain `run()` SHALL return a dict containing all output keys from every step in the sequence, not just the final step.

#### Scenario: Access intermediate step output
- **WHEN** a two-step SequentialChain runs where step 1 outputs {"topic": "Python"} and step 2 outputs {"summary": "..."}
- **THEN** the returned dict contains both {"topic": "Python", "summary": "..."}

### Requirement: SequentialChain input validation
SequentialChain SHALL validate that all declared `input_variables` are provided in the initial `run()` call, and that each chain's required input variables are satisfied by the initial inputs combined with prior step outputs.

#### Scenario: Missing initial input variable
- **WHEN** `run()` is called without providing all required input_variables
- **THEN** a KeyError is raised indicating which input variable is missing