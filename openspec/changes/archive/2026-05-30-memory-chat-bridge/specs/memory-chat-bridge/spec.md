## ADDED Requirements

### Requirement: Memory ABC defines load_messages
Memory ABC SHALL define an abstract `load_messages()` method that returns `List[BaseMessage]`. Each implementation SHALL return conversation history as a list of typed messages (HumanMessage, AIMessage) in chronological order.

#### Scenario: load_messages returns typed messages
- **WHEN** `memory.load_messages()` is called on a Memory instance with stored conversation history
- **THEN** the returned value SHALL be a list of BaseMessage instances

### Requirement: ConversationBufferMemory.load_messages returns full history
ConversationBufferMemory's `load_messages()` SHALL return all stored conversation turns as alternating HumanMessage/AIMessage pairs. Each call to `save_context(inputs, outputs)` SHALL produce one HumanMessage (from inputs) and one AIMessage (from outputs).

#### Scenario: Buffer memory returns message pairs
- **WHEN** ConversationBufferMemory has 2 stored turns: ("hi"→"hello"), ("bye"→"goodbye")
- **THEN** `load_messages()` SHALL return [HumanMessage("hi"), AIMessage("hello"), HumanMessage("bye"), AIMessage("goodbye")]

### Requirement: ConversationBufferWindowMemory.load_messages respects window size
ConversationBufferWindowMemory's `load_messages()` SHALL return only the most recent `k` turns as message pairs, matching the window behavior of `load_context()`.

#### Scenario: Window memory truncates old messages
- **WHEN** ConversationBufferWindowMemory(k=1) has 3 stored turns
- **THEN** `load_messages()` SHALL return only the most recent turn as a message pair (2 messages)

### Requirement: ConversationSummaryMemory.load_messages returns summary + recent
ConversationSummaryMemory's `load_messages()` SHALL return a HumanMessage containing the conversation summary, followed by recent message pairs from the buffer.

#### Scenario: Summary memory includes summary as HumanMessage
- **WHEN** ConversationSummaryMemory has a summary "User asked about Python" and one buffered turn
- **THEN** `load_messages()` SHALL include a HumanMessage whose content starts with the summary

### Requirement: load_context preserved unchanged
All Memory implementations SHALL keep their existing `load_context()` method returning a string. `load_messages()` is an additional method, not a replacement.

#### Scenario: load_context still works
- **WHEN** `memory.load_context()` is called after adding `load_messages()`
- **THEN** it SHALL return the same formatted string as before the change
