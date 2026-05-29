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


# ── Chat Message Types ───────────────────────────────────────────
class BaseMessage:
    """Base class for chat messages with role and content.

    Attributes:
        content: The text content of this message.
        role: The role of the message sender
            (``"system"``, ``"user"``, or ``"assistant"``).
    """

    def __init__(self, content: str, role: str) -> None:
        self.content = content
        self.role = role

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content={self.content!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseMessage):
            return NotImplemented
        return self.content == other.content and self.role == other.role


class SystemMessage(BaseMessage):
    """A message from the system to set the assistant's behavior."""

    def __init__(self, content: str) -> None:
        super().__init__(content=content, role="system")


class HumanMessage(BaseMessage):
    """A message from the human user."""

    def __init__(self, content: str) -> None:
        super().__init__(content=content, role="user")


class AIMessage(BaseMessage):
    """A message from the AI assistant."""

    def __init__(self, content: str) -> None:
        super().__init__(content=content, role="assistant")