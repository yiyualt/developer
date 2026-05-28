## ADDED Requirements

### Requirement: Async LLM support
LLM SHALL support async concurrent generation via ``agenerate(prompts: list[str]) -> list[str]`` async public method. Subclasses MAY implement ``_agenerate(prompts: list[str]) -> list[str]`` for concurrent generation; if ``_agenerate`` is not implemented, ``agenerate()`` SHALL fall back to calling ``generate()`` synchronously.

#### Scenario: Subclass implements _agenerate
- **WHEN** a class inherits from LLM and implements ``_agenerate(prompts: list[str]) -> list[str]``
- **THEN** calling ``agenerate(prompts)`` on that instance delegates to ``_agenerate`` and returns results concurrently

#### Scenario: Subclass does not implement _agenerate (fallback)
- **WHEN** a class inherits from LLM without implementing ``_agenerate`` and ``agenerate(prompts)`` is called
- **THEN** the method falls back to calling ``generate(prompts)`` synchronously

#### Scenario: Async generate preserves order
- **WHEN** ``agenerate(["prompt1", "prompt2", "prompt3"])`` is called on an LLM subclass that implements ``_agenerate``
- **THEN** responses are returned in the same order as input prompts