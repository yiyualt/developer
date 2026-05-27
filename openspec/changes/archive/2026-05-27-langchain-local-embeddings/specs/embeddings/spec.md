## ADDED Requirements

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