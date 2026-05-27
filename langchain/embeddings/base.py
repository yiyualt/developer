"""Embeddings - abstract base class for text embedding models.

Embeddings convert text into numerical vectors (lists of floats)
that capture semantic meaning. Similar texts produce similar vectors,
enabling similarity search in VectorStores.
"""

from abc import ABC, abstractmethod


class Embeddings(ABC):
    """Abstract base class for embedding models.

    Every Embeddings implementation must provide methods to
    convert single and multiple texts into their vector
    representations.
    """

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a vector.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the text's embedding vector.
        """
        ...

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings into vectors.

        Args:
            texts: A list of texts to embed.

        Returns:
            A list of embedding vectors, one per input text.
        """
        ...