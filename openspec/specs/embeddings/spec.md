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

### Requirement: LocalEmbeddings implementation
LocalEmbeddings SHALL implement the Embeddings ABC using a local sentence-transformers model. It SHALL accept an optional `model_name` parameter (default: "BAAI/bge-small-zh-v1.5"). The model SHALL be downloaded on first use and cached locally. `embed_text()` and `embed_texts()` SHALL use the loaded model to generate vectors without any API calls.

#### Scenario: Embed a single text locally
- **WHEN** LocalEmbeddings is initialized with default model_name and `embed_text("Hello world")` is called
- **THEN** a list of floats (embedding vector) is returned, dimension matching the model's output (512 for bge-small-zh-v1.5)

#### Scenario: Embed multiple texts locally
- **WHEN** `embed_texts(["Hello", "World"])` is called
- **THEN** a list of two embedding vectors is returned, each with the same dimension

#### Scenario: sentence-transformers not installed
- **WHEN** LocalEmbeddings is initialized and sentence-transformers is not available
- **THEN** an ImportError is raised with a message suggesting pip install sentence-transformers

#### Scenario: Custom model name
- **WHEN** LocalEmbeddings is created with model_name="all-MiniLM-L6-v2" and `embed_text("test")` is called
- **THEN** the specified model is loaded and vectors of its dimension are returned