## MODIFIED Requirements

### Requirement: OpenAI LLM implementation
OpenAI SHALL be a concrete LLM subclass that calls OpenAI Chat Completions API. Each input prompt string SHALL be sent as a single `user` message, and the response SHALL be the `content` field of the first choice. OpenAI SHALL implement `_stream(prompt: str) -> Generator[str, None, None]` using the OpenAI API with `stream=True`, yielding each token from the streaming response. OpenAI SHALL implement `_agenerate(prompts: list[str]) -> list[str]` using the AsyncOpenAI client with `asyncio.gather`, concurrently calling each prompt and returning results in input order.

#### Scenario: Generate single response via OpenAI
- **WHEN** OpenAI LLM is created with `model_name="gpt-4o-mini"` and `generate(["What is Python?"])` is called
- **THEN** the OpenAI Chat Completions API is called with one user message, and the first choice's content string is returned as the sole element in the response list

#### Scenario: Generate multiple responses via OpenAI
- **WHEN** OpenAI LLM is created and `generate(["prompt1", "prompt2"])` is called
- **THEN** the API is called for each prompt individually and a list of two response strings is returned

#### Scenario: Stream single prompt via OpenAI
- **WHEN** OpenAI LLM is created and `stream("What is Python?")` is called
- **THEN** the OpenAI Chat Completions API is called with `stream=True`, and tokens are yielded one at a time from the streaming response, and concatenating all tokens equals the full response

#### Scenario: Async generate multiple prompts via OpenAI
- **WHEN** OpenAI LLM is created and `agenerate(["prompt1", "prompt2", "prompt3"])` is called
- **THEN** the AsyncOpenAI client is used with asyncio.gather to concurrently call all three prompts, and responses are returned in the same order as input prompts