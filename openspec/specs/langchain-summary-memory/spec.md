## ADDED Requirements

### Requirement: ConversationSummaryMemory LLM compression
ConversationSummaryMemory SHALL implement the Memory ABC. It SHALL accept an `llm` parameter (LLM instance for generating summaries) and a `summary_prompt` parameter (default: a prompt template that instructs the LLM to summarize the conversation concisely, preserving key facts and decisions). Internally, it SHALL maintain `_buffer` (list of recent Human/AI pairs, same as ConversationBufferMemory) and `_summary` (str, the compressed history).

#### Scenario: Short conversation — no summary needed
- **WHEN** ConversationSummaryMemory is created, `save_context()` is called once with inputs={"question": "hi"} and outputs={"text": "hello"}, then `load_context()` is called
- **THEN** the raw buffer "Human: hi\nAI: hello" is returned (no summary generated, too short to compress)

#### Scenario: Long conversation triggers summarization
- **WHEN** ConversationSummaryMemory has `_buffer` with 3 rounds and `_summary` is empty, then `save_context()` is called with a 4th round
- **THEN** the LLM is called to compress all existing buffer content into a summary, `_buffer` is cleared, the new round is added to `_buffer`, and `_summary` is updated with the LLM's compressed output

#### Scenario: load_context returns summary + recent buffer
- **WHEN** `load_context()` is called after multiple rounds have been summarized
- **THEN** the returned string is `_summary` + "\n" + formatted recent `_buffer` entries, combining compressed history with the latest complete interactions

#### Scenario: Clear resets summary and buffer
- **WHEN** `clear()` is called
- **THEN** both `_summary` and `_buffer` are reset to empty state

### Requirement: ConversationSummaryMemory incremental summarization
When a new round is saved and `_summary` already exists, ConversationSummaryMemory SHALL not summarize from scratch. It SHALL send the existing `_summary` plus the new buffer entries to the LLM with a prompt that asks to "progressively update the summary with new information, preserving existing key facts."

#### Scenario: Incremental summary update
- **WHEN** `_summary` already contains "User asked about Python. Python is a programming language." and `save_context()` adds a new round about Python's creator
- **THEN** the LLM receives the existing summary + new round and returns an updated summary that includes both topics