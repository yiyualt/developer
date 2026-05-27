"""Memory - abstract base class for conversation history storage.

Memory provides a persistent conversation history that Chains and
Agents can automatically load and save across multiple run() calls.
"""

from abc import ABC, abstractmethod
from typing import Dict


class Memory(ABC):
    """Abstract base class for conversation memory.

    Every Memory implementation exposes three methods: save_context
    to store one round, load_context to return formatted history,
    and clear to reset stored history.
    """

    @abstractmethod
    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]) -> None:
        """Save one round of interaction to memory.

        Args:
            inputs: The input variables dict (e.g. {"question": "hi"}).
            outputs: The output dict (e.g. {"text": "hello"}).
        """
        ...

    @abstractmethod
    def load_context(self) -> str:
        """Return formatted conversation history as a string.

        Returns:
            A string of alternating Human/AI lines, ready to prepend
            to a prompt. Returns empty string if no history is stored.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Reset stored conversation history."""
        ...