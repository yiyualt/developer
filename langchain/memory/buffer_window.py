"""ConversationBufferWindowMemory - keep only the last K rounds."""

from typing import Dict, List

from langchain.memory.base import Memory
from langchain.schema import AIMessage, BaseMessage, HumanMessage


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

    def load_messages(self) -> List[BaseMessage]:
        """Return the last K rounds as alternating HumanMessage/AIMessage pairs.

        Returns:
            A list of at most 2*K messages. Empty list if no history.
        """
        recent = self._buffer[-self.k:]
        messages: List[BaseMessage] = []
        for human, ai in recent:
            messages.append(HumanMessage(content=human))
            messages.append(AIMessage(content=ai))
        return messages

    def clear(self) -> None:
        self._buffer.clear()