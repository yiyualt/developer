## ADDED Requirements

### Requirement: SelfCorrectingAgent wraps an Agent with validation-retry logic
SelfCorrectingAgent SHALL accept an `agent` (any Agent instance), a `corrector` (LLMCorrector), and `max_retries` (int, default 3). After the wrapped Agent produces an answer, the corrector SHALL check it. If the answer passes, it SHALL be returned immediately. If it fails, the corrector's feedback SHALL be appended to the original question and the Agent SHALL try again, up to `max_retries` times. The answer from the last attempt SHALL be returned regardless.

#### Scenario: Answer passes on first try
- **WHEN** agent produces a correct answer, and corrector returns (True, "")
- **THEN** the answer is returned immediately, and only 1 agent call is made

#### Scenario: Answer fails then passes on retry
- **WHEN** agent produces an incorrect answer, and corrector returns (False, "check formula"), and the retry produces a correct answer
- **THEN** the final answer is the corrected one, and the agent was called twice

#### Scenario: All retries fail
- **WHEN** max_retries=2 and both attempts fail validation
- **THEN** the last answer is returned (the corrector's check is advisory, not blocking)

### Requirement: LLMCorrector checks answer quality
LLMCorrector SHALL accept an `llm` parameter. Its `check(question, answer)` method SHALL ask the LLM to evaluate whether the answer is correct and complete. The LLM response starting with "PASS" (case-insensitive) SHALL indicate success; any other response SHALL indicate failure and be used as feedback.

#### Scenario: LLMCorrector returns pass
- **WHEN** LLM responds with "PASS" when asked to check an answer
- **THEN** `check()` SHALL return (True, "")

#### Scenario: LLMCorrector returns failure with feedback
- **WHEN** LLM responds with "The answer is wrong because..." when asked to check
- **THEN** `check()` SHALL return (False, "The answer is wrong because...")
