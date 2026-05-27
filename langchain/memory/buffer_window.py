"""ConversationBufferWindowMemory - keep only the last K rounds."""

from typing import Dict

from langchain.memory.base import Memory


class ConversationBufferWindowMemory(Memory):
    """Memory that stores conversation history but only returns the
    most recent K rounds via ``load_context()``.

    K represents the number of complete Human/AI pairs (rounds), not
    individual message count. Older rounds are dropped from the
    returned string but remain stored internally.
    """

    def __init__(self, k: int = 5) -> None:
        self.k = k
        self._buffer: list[tuple[str, str]] = []

    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]) -> None:
        human_msg = " ".join(f"{v}" for v in inputs.values())
        ai_msg = " ".join(f"{v}" for v in outputs.values())
        self._buffer.append((human_msg, ai_msg))

    def load_context(self) -> str:
        recent = self._buffer[-self.k:]
        if not recent:
            return ""
        lines = []
        for human, ai in recent:
            lines.append(f"Human: {human}")
            lines.append(f"AI: {ai}")
        return "\n".join(lines)

    def clear(self) -> None:
        self._buffer.clear()