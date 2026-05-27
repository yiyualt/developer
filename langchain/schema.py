"""Document - the fundamental unit of text content in LangChain.

Every loader, splitter, and vectorstore operates on Documents.
A Document holds a chunk of text (page_content) and optional
metadata about its origin (source, page number, etc.).
"""

from dataclasses import dataclass, field


@dataclass
class Document:
    """A piece of text content with associated metadata.

    Attributes:
        page_content: The text content of this document chunk.
        metadata: Optional dict of metadata (source, page, etc.).
    """

    page_content: str
    metadata: dict = field(default_factory=dict)