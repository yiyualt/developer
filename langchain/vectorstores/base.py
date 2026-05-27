"""VectorStore - abstract base class for vector-based document storage.

VectorStores index documents by their embedding vectors and
retrieve the most similar documents for a given query embedding.
"""

from abc import ABC, abstractmethod

from langchain.schema import Document


class VectorStore(ABC):
    """Abstract base class for vector-based document retrieval.

    Every VectorStore must support adding texts/documents with
    their embeddings and performing similarity search to find
    the k most relevant documents for a query.
    """

    @abstractmethod
    def add_texts(
        self,
        texts: list[str],
        metadatas: list[dict] | None = None,
        embeddings: list[list[float]] | None = None,
    ) -> None:
        """Add texts with their embedding vectors to the store.

        Args:
            texts: The text content to store.
            metadatas: Optional metadata dicts, one per text.
            embeddings: Pre-computed embedding vectors, one per text.
        """
        ...

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: list[float],
        k: int = 4,
    ) -> list[Document]:
        """Return the k most similar documents to the query.

        Args:
            query_embedding: The embedding vector of the query.
            k: Number of documents to return.

        Returns:
            A list of Documents sorted by similarity (most similar first).
        """
        ...

    @abstractmethod
    def add_documents(
        self,
        documents: list[Document],
        embeddings: list[list[float]],
    ) -> None:
        """Add Document objects with their embeddings.

        Args:
            documents: Documents to store.
            embeddings: Embedding vectors, one per document.
        """
        ...