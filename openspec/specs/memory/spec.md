## ADDED Requirements

### Requirement: Memory ABC interface
Memory SHALL be an abstract base class defining three methods: `save_context(inputs: dict, outputs: dict)` to store a round of interaction, `load_context() -> str` to return formatted conversation history, and `clear()` to reset stored history. ConversationSummaryMemory extends this interface by accepting an `llm` parameter and maintaining an internal `_summary` state alongside `_buffer`, enabling LLM-powered history compression.

#### Scenario: Subclass implements Memory
- **WHEN** a subclass of Memory is created with save_context, load_context, and clear methods
- **THEN** it can save an interaction via `save_context({"question": "hi"}, {"text": "hello"})`, retrieve formatted history via `load_context()` returning `"Human: hi\nAI: hello"`, and reset via `clear()`

#### Scenario: SummaryMemory is a valid Memory implementation
- **WHEN** ConversationSummaryMemory is created with an LLM instance
- **THEN** it can be used as a `memory` parameter for LLMChain and Agent, just like ConversationBufferMemory

### Requirement: ConversationBufferMemory
ConversationBufferMemory SHALL store the complete conversation history as a list of Human/AI message pairs. `load_context()` SHALL return all stored messages formatted as alternating `"Human: {input}\nAI: {output}"` lines.

#### Scenario: Multi-round conversation
- **WHEN** ConversationBufferMemory saves three rounds of interactions
- **THEN** `load_context()` returns all three rounds formatted as `"Human: ...\nAI: ...\nHuman: ...\nAI: ...\nHuman: ...\nAI: ..."`

#### Scenario: Clear history
- **WHEN** `clear()` is called on a ConversationBufferMemory with stored history
- **THEN** subsequent `load_context()` returns an empty string

### Requirement: ConversationBufferWindowMemory
ConversationBufferWindowMemory SHALL store conversation history but only return the most recent K rounds via `load_context()`. K is configured at construction time.

#### Scenario: Window truncation
- **WHEN** ConversationBufferWindowMemory is created with k=2 and 5 rounds are saved
- **THEN** `load_context()` returns only the last 2 rounds, the first 3 rounds are excluded from the returned string

#### Scenario: K equals total rounds
- **WHEN** ConversationBufferWindowMemory is created with k=5 and 3 rounds are saved
- **THEN** `load_context()` returns all 3 rounds (no truncation needed)

### Requirement: Memory load_messages for Chat Model bridge
Memory SHALL define an abstract `load_messages() -> List[BaseMessage]` method. Each implementation SHALL return conversation history as alternating HumanMessage/AIMessage pairs. ConversationSummaryMemory SHALL wrap its summary in a HumanMessage. The existing `load_context() -> str` method SHALL be preserved unchanged.

#### Scenario: BufferMemory returns message pairs
- **WHEN** ConversationBufferMemory has stored turns ("hi"→"hello"), ("bye"→"goodbye")
- **THEN** `load_messages()` SHALL return [HumanMessage("hi"), AIMessage("hello"), HumanMessage("bye"), AIMessage("goodbye")]

#### Scenario: WindowMemory respects k in messages
- **WHEN** ConversationBufferWindowMemory(k=1) has 3 stored turns
- **THEN** `load_messages()` SHALL return only 2 messages (the most recent round)