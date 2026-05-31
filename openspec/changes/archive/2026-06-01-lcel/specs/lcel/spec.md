## ADDED Requirements

### Requirement: Runnable ABC defines invoke interface
Runnable SHALL be an abstract base class with an abstract `invoke(input: Any) -> Any` method and a `__or__` method that returns a RunnableSequence.

#### Scenario: Two runnables piped create RunnableSequence
- **WHEN** `a | b` is called where a and b are Runnable instances
- **THEN** the result SHALL be a RunnableSequence with steps [a, b]

### Requirement: RunnableSequence executes steps in order
RunnableSequence SHALL accept any number of Runnable steps and execute them in order when `invoke()` is called, passing each step's output as the next step's input.

#### Scenario: Three-step pipeline
- **WHEN** `RunnableSequence(a, b, c).invoke("input")` is called
- **THEN** `a.invoke("input")` returns X, `b.invoke(X)` returns Y, `c.invoke(Y)` returns Z, and the final result is Z

### Requirement: PromptTemplate implements Runnable
PromptTemplate SHALL implement Runnable. `invoke(input_vars: dict)` SHALL call `format(**input_vars)` and return the formatted string.

#### Scenario: PromptTemplate.invoke formats template
- **WHEN** `PromptTemplate("Hello {name}").invoke({"name": "World"})` is called
- **THEN** the result SHALL be "Hello World"

### Requirement: LLM implements Runnable
LLM ABC SHALL implement Runnable. `invoke(prompt: str)` SHALL call `generate([prompt])` and return the first response string.

#### Scenario: LLM.invoke generates response
- **WHEN** `llm.invoke("What is Python?")` is called
- **THEN** the result SHALL be the LLM's response string

### Requirement: OutputParser implements Runnable
OutputParser SHALL implement Runnable. `invoke(text: str)` SHALL call `parse(text)` and return the parsed result.

### Requirement: LCEL pipeline works end-to-end
`PromptTemplate | LLM` SHALL produce a Runnable that formats a prompt and generates a response. `PromptTemplate | LLM | OutputParser` SHALL additionally parse the response.

#### Scenario: prompt | llm pipeline
- **WHEN** `(PromptTemplate("Say {word}") | llm).invoke({"word": "hello"})` is called
- **THEN** the LLM receives "Say hello" and returns its response
