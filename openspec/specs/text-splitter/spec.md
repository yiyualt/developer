## ADDED Requirements

### Requirement: TextSplitter splits documents into chunks
TextSplitter SHALL accept `chunk_size` (int, max characters per chunk) and `chunk_overlap` (int, characters overlapping between adjacent chunks). It SHALL provide a `split_text(text: str) -> list[str]` method that splits text into chunks of approximately `chunk_size` characters, with `chunk_overlap` characters shared between consecutive chunks.

#### Scenario: Split text with overlap
- **WHEN** TextSplitter is created with chunk_size=100, chunk_overlap=20, and `split_text()` is called on a 250-character string
- **THEN** approximately 3 chunks are returned, each ≤100 characters, with ~20 overlap characters between consecutive chunks

#### Scenario: Split text shorter than chunk_size
- **WHEN** TextSplitter is created with chunk_size=1000 and `split_text()` is called on a 50-character string
- **THEN** a list containing the original string as one chunk is returned

### Requirement: TextSplitter splits Documents
TextSplitter SHALL provide a `split_documents(documents: list[Document]) -> list[Document]` method that splits each Document's `page_content` into chunks. Each resulting Document SHALL inherit the original Document's `metadata`.

#### Scenario: Split a list of Documents
- **WHEN** `split_documents()` is called on a list of 2 Documents, each with 500 characters of content, and TextSplitter has chunk_size=200
- **THEN** approximately 5 Documents are returned, each with ≤200 characters, all inheriting the original metadata