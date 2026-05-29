## ADDED Requirements

### Requirement: Message types represent chat roles
The system SHALL provide `BaseMessage` (dataclass with `content` and `role`), `SystemMessage` (role="system"), `HumanMessage` (role="user"), and `AIMessage` (role="assistant"). Each SHALL be a dataclass with `content: str` and `role: str` fields.

#### Scenario: Create system message
- **WHEN** `SystemMessage(content="You are a helpful assistant")` is created
- **THEN** `msg.role` SHALL be `"system"` and `msg.content` SHALL be `"You are a helpful assistant"`

#### Scenario: Create human message
- **WHEN** `HumanMessage(content="What is Python?")` is created
- **THEN** `msg.role` SHALL be `"user"`

#### Scenario: Create AI message
- **WHEN** `AIMessage(content="Python is a programming language")` is created
- **THEN** `msg.role` SHALL be `"assistant"`

### Requirement: ChatPromptTemplate formats message templates
ChatPromptTemplate SHALL accept a list of BaseMessage instances where each message's content may contain `{variable}` placeholders. The `format(**kwargs)` method SHALL return a list of BaseMessage instances with all variables substituted. The original message SHALL NOT be mutated.

#### Scenario: Format chat prompt with system and human messages
- **WHEN** `ChatPromptTemplate([SystemMessage("You are a {role}"), HumanMessage("Explain {topic}")]).format(role="math tutor", topic="calculus")` is called
- **THEN** the result SHALL be `[SystemMessage("You are a math tutor"), HumanMessage("Explain calculus")]`

#### Scenario: ChatPromptTemplate preserves message types
- **WHEN** ChatPromptTemplate formats messages
- **THEN** each formatted message SHALL be an instance of the same subclass as the original template message

### Requirement: OpenAI supports generate_messages
OpenAI SHALL provide a `generate_messages(messages_list: list[list[BaseMessage]]) -> list[str]` method. Each inner list of messages SHALL be sent to the Chat Completions API with correct roles. The response SHALL be the content of the first choice.

#### Scenario: Generate from chat messages
- **WHEN** `openai.generate_messages([[SystemMessage("You are helpful"), HumanMessage("Say hi")]])` is called
- **THEN** the API SHALL receive `messages=[{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "Say hi"}]` and return the LLM response
