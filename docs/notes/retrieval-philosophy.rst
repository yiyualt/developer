Retrieval Philosophy
====================

LLMs are powerful but limited — they can only answer from their
training data. No access to private documents, no real-time
information, no domain-specific knowledge that wasn't in the
training corpus.

RAG (Retrieval-Augmented Generation) breaks this boundary by
injecting external knowledge into the LLM's prompt at runtime.

The core idea is simple: before generating, first *retrieve*.

The RAG pipeline
-----------------

.. code-block:: text

   Question → Embed → Vector Search → Retrieve Docs
                                              │
                                              ▼
   Answer ← LLM ← Prompt ← Context + Question

   Step 1: Embed the user's question into a vector
   Step 2: Search the VectorStore for similar document chunks
   Step 3: Concatenate retrieved chunks as "context"
   Step 4: Inject context into the prompt alongside the question
   Step 5: LLM generates an answer grounded in retrieved facts

Why not just put all documents in the prompt?
-----------------------------------------------

Because prompts have length limits. A 100-page document can't
fit in a single prompt. RAG solves this by *selectively*
retrieving only the relevant passages, keeping the prompt
concise while still providing the LLM with the right context.

Document → Chunk → Embed → Store
----------------------------------

Raw documents must be processed before they can be searched:

1. **DocumentLoader** reads files into Document objects
2. **TextSplitter** cuts long documents into smaller chunks
   (because embedding and retrieval work best on focused passages)
3. **Embeddings** converts each chunk into a vector
4. **VectorStore** indexes the vectors for similarity search

The chunking step is critical — too large and the search loses
precision; too small and each chunk lacks enough context. The
overlap between consecutive chunks preserves continuity.

SimpleVectorStore: why numpy?
------------------------------

Early LangChain used FAISS for vector search. But FAISS has
installation issues on macOS and adds complexity that obscures
the core idea.

SimpleVectorStore uses numpy cosine similarity instead. This
makes the math transparent:

.. code-block:: text

   similarity = dot(query, doc) / (norm(query) * norm(doc))

   ┌─────────┐         ┌─────────┐
   │ Query   │   dot   │ Chunk 1 │ → 0.92 (most similar)
   │ Vector  │ ─────── │ Chunk 2 │ → 0.45
   │         │         │ Chunk 3 │ → 0.31
   └─────────┘         └─────────┘

   Top-k selection: sort by similarity, take the first k.

The tradeoff: SimpleVectorStore is in-memory, no persistence,
and linear-time search. Fine for teaching and prototyping;
FAISS or ChromaDB come later for production scale.

Embeddings: local vs API
-------------------------

Two Embeddings implementations are available:

.. code-block:: text

   LocalEmbeddings              DashScopeEmbeddings
   ──────────────────────       ──────────────────────
   sentence-transformers        DashScope API (cloud)
   Downloads model on first run Requires API key + permissions
   Runs offline after download   Needs network every call
   bge-small-zh-v1.5 (default)  text-embedding-v3 (default)
   512-dim vectors              API-dependent dimensions
   No API key needed            Shares .env with LLM

   Use LocalEmbeddings when:    Use DashScopeEmbeddings when:
   - DashScope API unavailable  - You have API access
   - Offline/low-latency needed - Cloud consistency matters
   - Teaching/prototyping       - Production deployment

LocalEmbeddings is the recommended default for getting started
— it works out of the box without any API configuration.
DashScopeEmbeddings is available for accounts with embedding
API permissions enabled in the DashScope console.

What we don't have yet
-----------------------

- RecursiveCharacterTextSplitter (better chunk boundaries)
- Metadata filtering (search within a subset)
- Hybrid search (combine keyword + vector)
- Persistent vector stores (FAISS, ChromaDB)

These are all later evolutions in the LangChain history.
The current version captures the earliest, simplest form of RAG.