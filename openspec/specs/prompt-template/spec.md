## ADDED Requirements

### Requirement: PromptTemplate variable substitution
PromptTemplate SHALL accept a template string with `{variable_name}` placeholders and substitute them with provided values to produce a complete prompt string.

#### Scenario: Simple variable substitution
- **WHEN** PromptTemplate is created with template `"Hello {name}!"` and `format(name="World")` is called
- **THEN** the result is `"Hello World!"`

#### Scenario: Multiple variable substitution
- **WHEN** PromptTemplate is created with template `"Tell me about {topic} in {style}"` and `format(topic="Python", style="simple")` is called
- **THEN** the result is `"Tell me about Python in simple"`

### Requirement: PromptTemplate input variable extraction
PromptTemplate SHALL automatically extract input variable names from the template string and store them as `input_variables`.

#### Scenario: Extract single variable
- **WHEN** PromptTemplate is created with template `"What is {question}?"`
- **THEN** `input_variables` equals `["question"]`

#### Scenario: Extract multiple variables
- **WHEN** PromptTemplate is created with template `"Write about {topic} in {language}"`
- **THEN** `input_variables` equals `["topic", "language"]`

### Requirement: PromptTemplate validation
PromptTemplate SHALL validate that all provided input variables match the variables defined in the template, raising an error on mismatch.

#### Scenario: Missing required variable
- **WHEN** PromptTemplate with template `"Hello {name} and {place}"` is called with `format(name="Alice")`
- **THEN** an error is raised indicating that `place` is missing

#### Scenario: Extra unexpected variable
- **WHEN** PromptTemplate with template `"Hello {name}"` is called with `format(name="Alice", age=30)`
- **THEN** an error is raised indicating that `age` is not an input variable