"""SimpleVectorStore - in-memory vector store using numpy cosine similarity.

SimpleVectorStore stores texts, metadata, and embedding vectors
in plain Python lists and uses numpy to compute cosine similarity
for retrieval. This is the simplest possible implementation —
no external database, no persistence, suitable for teaching
and small-scale prototyping.
"""

import numpy as np

from langchain.schema import Document
from langchain.vectorstores.base import VectorStore


class SimpleVectorStore(VectorStore):
    """In-memory vector store with numpy cosine similarity.

    Stores all data in Python lists. Similarity search computes
    cosine similarity between the query embedding and every
    stored embedding, then returns the top-k matches.

    Args:
        No constructor arguments — all data lives in memory.
    """

    def __init__(self) -> None:
        self._texts: list[str] = []
        self._metadatas: list[dict] = []
        self._embeddings: list[list[float]] = []

    def add_texts(
        self,
        texts: list[str],
        metadatas: list[dict] | None = None,
        embeddings: list[list[float]] | None = None,
    ) -> None:
        if embeddings is None:
            raise ValueError("SimpleVectorStore requires pre-computed embeddings.")
        if len(texts) != len(embeddings):
            raise ValueError(
                f"Number of texts ({len(texts)}) must match number of "
                f"embeddings ({len(embeddings)})."
            )
        metadatas = metadatas or [{} for _ in texts]
        for text, meta, emb in zip(texts, metadatas, embeddings):
            self._texts.append(text)
            self._metadatas.append(meta)
            self._embeddings.append(emb)

    def similarity_search(
        self,
        query_embedding: list[float],
        k: int = 4,
    ) -> list[Document]:
        if not self._texts:
            return []

        stored = np.array(self._embeddings)
        query = np.array(query_embedding)

        # Cosine similarity: dot product / (norm * norm)
        norms_stored = np.linalg.norm(stored, axis=1)
        norm_query = np.linalg.norm(query)
        similarities = np.dot(stored, query) / (norms_stored * norm_query)

        # Top-k indices (highest similarity first)
        top_indices = np.argsort(similarities)[::-1][:k]

        return [
            Document(
                page_content=self._texts[i],
                metadata=self._metadatas[i],
            )
            for i in top_indices
        ]

    def add_documents(
        self,
        documents: list[Document],
        embeddings: list[list[float]],
    ) -> None:
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        self.add_texts(texts, metadatas, embeddings)