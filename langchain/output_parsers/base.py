"""OutputParser base class - the abstract interface for parsing LLM output.

LLMs return free-form text strings. OutputParser converts those strings
into structured Python data that programs can use — dicts, lists, enums, etc.
"""

from abc import ABC, abstractmethod
from typing import Any


class OutputParser(ABC):
    """Abstract base class for LLM output parsers.

    All OutputParser subclasses MUST implement the ``parse`` method,
    which accepts a raw LLM response string and returns a structured
    Python object.

    Examples:
        Subclass implementation::

            from langchain.output_parsers import OutputParser

            class MyParser(OutputParser):
                def parse(self, text: str) -> Any:
                    return text.strip().lower()
    """

    @abstractmethod
    def parse(self, text: str) -> Any:
        """Parse a raw LLM response string into a structured Python object.

        Args:
            text: The raw text output from an LLM call.

        Returns:
            A parsed Python object (dict, list, str, etc.).

        Raises:
            ValueError: If the text cannot be parsed into the expected format.
        """