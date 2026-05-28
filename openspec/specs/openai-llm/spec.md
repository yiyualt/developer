## MODIFIED Requirements

### Requirement: OpenAI LLM implementation
OpenAI SHALL be a concrete LLM subclass that calls OpenAI Chat Completions API. Each input prompt string SHALL be sent as a single `user` message, and the response SHALL be the `content` field of the first choice. OpenAI SHALL implement `_stream(prompt: str) -> Generator[str, None, None]` using the OpenAI API with `stream=True`, yielding each token from the streaming response.

#### Scenario: Generate single response via OpenAI
- **WHEN** OpenAI LLM is created with `model_name="gpt-4o-mini"` and `generate(["What is Python?"])` is called
- **THEN** the OpenAI Chat Completions API is called with one user message, and the first choice's content string is returned as the sole element in the response list

#### Scenario: Generate multiple responses via OpenAI
- **WHEN** OpenAI LLM is created and `generate(["prompt1", "prompt2"])` is called
- **THEN** the API is called for each prompt individually and a list of two response strings is returned

#### Scenario: Stream single prompt via OpenAI
- **WHEN** OpenAI LLM is created and `stream("What is Python?")` is called
- **THEN** the OpenAI Chat Completions API is called with `stream=True`, and tokens are yielded one at a time from the streaming response, and concatenating all tokens equals the full response

### Requirement: OpenAI model selection
OpenAI LLM SHALL accept a `model_name` parameter that determines which OpenAI model to use. The default SHALL be `gpt-4o-mini`.

#### Scenario: Use default model
- **WHEN** OpenAI LLM is created without specifying `model_name`
- **THEN** Chat Completions API calls use `gpt-4o-mini` as the model

#### Scenario: Use specified model
- **WHEN** OpenAI LLM is created with `model_name="gpt-4o"`
- **THEN** Chat Completions API calls use `gpt-4o` as the model

### Requirement: OpenAI generation parameters
OpenAI LLM SHALL accept `temperature` and `max_tokens` parameters that are passed through to the Chat Completions API.

#### Scenario: Temperature control
- **WHEN** OpenAI LLM is created with `temperature=0`
- **THEN** Chat Completions API calls include `temperature=0` producing deterministic responses

#### Scenario: Max tokens control
- **WHEN** OpenAI LLM is created with `max_tokens=100`
- **THEN** Chat Completions API calls include `max_tokens=100` limiting response length

### Requirement: OpenAI API key configuration
OpenAI LLM SHALL accept the API key via `openai_api_key` constructor parameter or `OPENAI_API_KEY` environment variable. The constructor parameter SHALL take precedence.

#### Scenario: API key from environment variable
- **WHEN** OpenAI LLM is created without `openai_api_key` and `OPENAI_API_KEY` environment variable is set
- **THEN** the environment variable value is used as the API key

#### Scenario: API key from constructor
- **WHEN** OpenAI LLM is created with `openai_api_key="sk-xxx"`
- **THEN** that value is used as the API key regardless of environment variable

#### Scenario: No API key available
- **WHEN** OpenAI LLM is created without `openai_api_key` and `OPENAI_API_KEY` is not set
- **THEN** calling `generate` raises a ValueError indicating the API key is missing