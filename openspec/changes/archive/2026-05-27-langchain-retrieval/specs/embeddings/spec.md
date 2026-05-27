## ADDED Requirements

### Requirement: Embeddings abstract interface
Embeddings SHALL define an ABC with an `embed_text(text: str) -> list[float]` method that returns a vector (list of floats) for a single text, and an `embed_texts(texts: list[str]) -> list[list[float]]` method that returns vectors for multiple texts.

#### Scenario: ABC enforces embed methods
- **WHEN** a class inherits Embeddings but does not implement `embed_text()` and `embed_texts()`
- **THEN** instantiation raises TypeError

### Requirement: DashScope embedding implementation
DashScopeEmbeddings SHALL implement Embeddings using DashScope's OpenAI-compatible embedding API. It SHALL read `LLM_API_KEY` and `LLM_BASE_URL` from the `.env` file (same configuration as the LLM). `embed_texts()` SHALL batch requests when possible.

#### Scenario: Embed a single text
- **WHEN** DashScopeEmbeddings is initialized and `embed_text("Hello world")` is called
- **THEN** a list of floats (embedding vector) is returned with dimension matching the DashScope model output

#### Scenario: Embed multiple texts
- **WHEN** `embed_texts(["Hello", "World"])` is called
- **THEN** a list of two embedding vectors is returned, each with the same dimension

#### Scenario: Handle API failure
- **WHEN** `embed_text()` is called and the DashScope API returns an error
- **THEN** an exception is raised with a descriptive error message