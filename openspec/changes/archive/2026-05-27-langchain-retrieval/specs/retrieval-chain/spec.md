## ADDED Requirements

### Requirement: RetrievalChain composition
RetrievalChain SHALL compose a VectorStore, an Embeddings instance, and an LLMChain into an end-to-end RAG pipeline. It SHALL accept `vectorstore`, `embeddings`, and `llm_chain` as constructor parameters. The LLMChain's prompt SHALL contain a `{context}` variable where retrieved documents are injected.

#### Scenario: Execute a RAG query
- **WHEN** RetrievalChain is created with a VectorStore containing stored documents, an Embeddings instance, and an LLMChain whose prompt template includes `{context}` and `{question}`
- **THEN** calling `run(question="What is LangChain?")` SHALL: (1) embed the question, (2) retrieve relevant documents from the VectorStore, (3) concatenate their content as context, (4) pass context and question to the LLMChain, (5) return the LLM's answer

### Requirement: RetrievalChain context formatting
RetrievalChain SHALL format retrieved documents into a single context string by concatenating their `page_content` with a separator (default: "\n\n"). The context string SHALL be passed as the `context` variable to the LLMChain.

#### Scenario: Format retrieved context
- **WHEN** RetrievalChain retrieves 3 Documents with page_content "doc1", "doc2", "doc3"
- **THEN** the context variable passed to LLMChain equals "doc1\n\ndoc2\n\ndoc3"

### Requirement: RetrievalChain k parameter
RetrievalChain SHALL accept a `k` parameter (default: 4) that controls how many documents are retrieved from the VectorStore per query.

#### Scenario: Retrieve top-k documents
- **WHEN** RetrievalChain is created with k=2 and `run(question="...")` is called
- **THEN** only the 2 most similar documents are retrieved and injected as context