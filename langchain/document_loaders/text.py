"""TextLoader - load plain text files into LangChain Documents."""

from langchain.document_loaders.base import DocumentLoader
from langchain.schema import Document


class TextLoader(DocumentLoader):
    """Load a plain text file as a single Document.

    Args:
        file_path: Path to the text file to load.

    The loaded Document's metadata will contain {"source": file_path}.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def load(self) -> list[Document]:
        """Read the text file and return a list containing one Document.

        Returns:
            A list with one Document whose page_content is the file
            contents and metadata includes the source file path.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        with open(self.file_path, encoding="utf-8") as f:
            text = f.read()
        return [Document(page_content=text, metadata={"source": self.file_path})]