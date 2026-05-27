"""LocalEmbeddings - local embedding model via sentence-transformers.

Uses a locally-downloaded model from sentence-transformers to
generate embeddings without any API calls. Ideal for prototyping
and offline use.
"""

from langchain.embeddings.base import Embeddings


class LocalEmbeddings(Embeddings):
    """Embedding model using a local sentence-transformers model.

    Downloads the model on first use, then runs entirely offline.
    No API key required.

    Args:
        model_name: The sentence-transformers model name.
            Defaults to ``BAAI/bge-small-zh-v1.5`` — a compact
            model with strong Chinese+English similarity performance.

    Raises:
        ImportError: If sentence-transformers is not installed.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5") -> None:
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for LocalEmbeddings. "
                "Install it with: pip install sentence-transformers"
            )
        self._model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string.

        Args:
            text: The text to embed.

        Returns:
            A list of floats (the embedding vector).
        """
        return self._model.encode(text).tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings efficiently.

        Args:
            texts: A list of texts to embed.

        Returns:
            A list of embedding vectors, one per input text.
        """
        embeddings = self._model.encode(texts)
        return [e.tolist() for e in embeddings]