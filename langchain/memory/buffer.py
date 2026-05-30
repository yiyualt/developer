"""ConversationBufferMemory - store complete conversation history."""

from typing import Dict, List

from langchain.memory.base import Memory
from langchain.schema import AIMessage, BaseMessage, HumanMessage


class ConversationBufferMemory(Memory):
    """Memory that stores the complete conversation history.

    Every round is saved as a Human/AI pair and returned in full by
    ``load_context()``. Use ConversationBufferWindowMemory instead
    if you need to truncate older history.
    """

    def __init__(self) -> None:
        self._buffer: list[tuple[str, str]] = []

    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]) -> None:
        human_msg = " ".join(f"{v}" for v in inputs.values())
        ai_msg = " ".join(f"{v}" for v in outputs.values())
        self._buffer.append((human_msg, ai_msg))

    def load_context(self) -> str:
        if not self._buffer:
            return ""
        lines = []
        for human, ai in self._buffer:
            lines.append(f"Human: {human}")
            lines.append(f"AI: {ai}")
        return "\n".join(lines)

    def load_messages(self) -> List[BaseMessage]:
        """Return complete history as alternating HumanMessage/AIMessage pairs.

        Returns:
            A list of HumanMessage and AIMessage instances in
            chronological order. Empty list if no history.
        """
        messages: List[BaseMessage] = []
        for human, ai in self._buffer:
            messages.append(HumanMessage(content=human))
            messages.append(AIMessage(content=ai))
        return messages

    def clear(self) -> None:
        self._buffer.clear()