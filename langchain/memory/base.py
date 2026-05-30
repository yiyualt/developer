"""Memory - abstract base class for conversation history storage.

Memory provides a persistent conversation history that Chains and
Agents can automatically load and save across multiple run() calls.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from langchain.schema import BaseMessage


class Memory(ABC):
    """Abstract base class for conversation memory.

    Every Memory implementation exposes four methods: save_context
    to store one round, load_context to return formatted history
    as a string, load_messages to return history as typed messages,
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
    def load_messages(self) -> List[BaseMessage]:
        """Return conversation history as typed chat messages.

        Returns:
            A list of BaseMessage instances (HumanMessage, AIMessage)
            in chronological order. Returns empty list if no history.

            Use this method when working with Chat Model's
            ``generate_messages()`` — the message roles are
            preserved instead of being flattened into a string.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Reset stored conversation history."""
        ...