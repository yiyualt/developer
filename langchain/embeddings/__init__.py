"""Embeddings - convert text into vector representations."""

from langchain.embeddings.base import Embeddings
from langchain.embeddings.dashscope import DashScopeEmbeddings
from langchain.embeddings.local import LocalEmbeddings

__all__ = ["Embeddings", "DashScopeEmbeddings", "LocalEmbeddings"]