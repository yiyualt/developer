"""DocumentLoaders - load external files into LangChain Documents."""

from langchain.document_loaders.base import DocumentLoader
from langchain.document_loaders.text import TextLoader
from langchain.schema import Document

__all__ = ["DocumentLoader", "TextLoader", "Document"]