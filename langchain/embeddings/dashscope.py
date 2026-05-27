"""DashScopeEmbeddings - text embeddings via DashScope's OpenAI-compatible API.

Uses the same .env configuration as the LLM (LLM_API_KEY, LLM_BASE_URL)
and calls the /embeddings endpoint to convert text into vectors.
"""

import os
from pathlib import Path
from typing import Optional

import openai
from dotenv import load_dotenv

from langchain.embeddings.base import Embeddings

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class DashScopeEmbeddings(Embeddings):
    """Embedding model using DashScope's OpenAI-compatible API.

    Configuration follows the same pattern as the OpenAI LLM:
    constructor parameters > .env file > environment variables.

    Args:
        model_name: Embedding model to use. Defaults to
            ``LLM_EMBEDDING_MODEL`` env var or ``text-embedding-v3``.
        openai_api_key: API key. Defaults to ``LLM_API_KEY`` or
            ``OPENAI_API_KEY`` env var.
        base_url: API endpoint URL. Defaults to ``LLM_BASE_URL``
            or ``OPENAI_BASE_URL`` env var.

    Raises:
        ValueError: If no API key is available.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.model_name = (
            model_name or os.environ.get("LLM_EMBEDDING_MODEL") or "text-embedding-v3"
        )
        self.openai_api_key = (
            openai_api_key
            or os.environ.get("LLM_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        self.base_url = (
            base_url
            or os.environ.get("LLM_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
        )
        if not self.openai_api_key:
            raise ValueError(
                "API key not found. Set LLM_API_KEY in .env file, "
                "environment variable, or pass openai_api_key parameter."
            )
        self._client = openai.OpenAI(
            api_key=self.openai_api_key,
            base_url=self.base_url,
        )

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string.

        Args:
            text: The text to embed.

        Returns:
            A list of floats (the embedding vector).
        """
        response = self._client.embeddings.create(
            model=self.model_name,
            input=text,
        )
        return response.data[0].embedding

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings.

        Args:
            texts: A list of texts to embed.

        Returns:
            A list of embedding vectors, one per input text.
        """
        response = self._client.embeddings.create(
            model=self.model_name,
            input=texts,
        )
        return [item.embedding for item in response.data]