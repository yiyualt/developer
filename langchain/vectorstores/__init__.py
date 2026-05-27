"""VectorStores - store and retrieve documents by similarity."""

from langchain.vectorstores.base import VectorStore
from langchain.vectorstores.simple import SimpleVectorStore

__all__ = ["VectorStore", "SimpleVectorStore"]