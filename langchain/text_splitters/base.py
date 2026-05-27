"""TextSplitter - split text into overlapping chunks for retrieval.

Fixed-length character splitting is the earliest approach LangChain
used. It cuts text at a given character count with optional overlap
between consecutive chunks, which preserves some context across
chunk boundaries.
"""

from langchain.schema import Document


class TextSplitter:
    """Split text into chunks of approximately chunk_size characters.

    Args:
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of overlapping characters between
            consecutive chunks. Overlap helps preserve context
            across chunk boundaries.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """Split a single text string into overlapping chunks.

        Args:
            text: The text to split.

        Returns:
            A list of text chunks, each ≤ chunk_size characters.
            If the text is shorter than chunk_size, returns
            [text] unchanged.
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Split each Document's page_content into chunks.

        Each resulting Document inherits the original's metadata.

        Args:
            documents: A list of Documents to split.

        Returns:
            A list of Documents, each containing a text chunk
            and the original metadata.
        """
        result = []
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            for chunk in chunks:
                result.append(Document(page_content=chunk, metadata=doc.metadata))
        return result