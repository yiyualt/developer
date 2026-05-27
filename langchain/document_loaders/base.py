"""DocumentLoader - abstract base class for loading documents.

Every DocumentLoader takes a source (file path, URL, etc.) and
produces a list of Document objects via its load() method.
"""

from abc import ABC, abstractmethod

from langchain.schema import Document


class DocumentLoader(ABC):
    """Abstract base class for document loading.

    Subclass DocumentLoader to create loaders for different file
    formats. Each loader must implement load() to return a list
    of Document objects.
    """

    @abstractmethod
    def load(self) -> list[Document]:
        """Load documents from the source.

        Returns:
            A list of Document objects containing the loaded content.
        """
        ...