"""ConversationBufferMemory - store complete conversation history."""

from typing import Dict

from langchain.memory.base import Memory


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

    def clear(self) -> None:
        self._buffer.clear()