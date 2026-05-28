"""ConversationSummaryMemory - compress conversation history with LLM summarization.

ConversationBufferMemory stores everything, which grows indefinitely.
ConversationSummaryMemory solves this by periodically compressing
older history into a concise summary using an LLM, preserving key
facts and decisions while keeping the prompt length bounded.

The internal state is:
- _summary: str — the compressed history (accumulated over time)
- _buffer: list[tuple[str, str]] — recent rounds not yet summarized

load_context() returns _summary + formatted recent _buffer,
giving the LLM both the compressed past and the latest interactions.
"""

from typing import Dict

from langchain.chains.llm_chain import LLMChain
from langchain.llms.base import LLM
from langchain.memory.base import Memory
from langchain.prompts.prompt import PromptTemplate


INITIAL_SUMMARY_PROMPT = PromptTemplate(
    template="Summarize the following conversation concisely, "
             "preserving key facts, decisions, and important details. "
             "Do not add information that was not discussed.\n\n"
             "Conversation:\n{conversation}\n\nSummary:",
)

INCREMENTAL_SUMMARY_PROMPT = PromptTemplate(
    template="You have an existing summary of a conversation. "
             "New exchanges have occurred. Update the summary to "
             "include the new information while preserving all "
             "existing key facts. Do not add information that was "
             "not discussed.\n\n"
             "Existing summary:\n{summary}\n\n"
             "New exchanges:\n{new_exchanges}\n\n"
             "Updated summary:",
)


class ConversationSummaryMemory(Memory):
    """Memory that compresses conversation history into a LLM-generated summary.

    Older rounds are periodically compressed into a concise summary.
    load_context() returns the summary plus recent un-summarized rounds,
    keeping prompt length bounded while preserving key information.

    Args:
        llm: An LLM instance used for generating summaries.
        max_buffer_rounds: Maximum number of rounds to keep in the
            buffer before triggering summarization. Default is 2.
            When buffer exceeds this, all buffered rounds are
            compressed into the summary.

    Examples:
        >>> from langchain import ConversationSummaryMemory, OpenAI
        >>> memory = ConversationSummaryMemory(llm=OpenAI())
        >>> chain = LLMChain(prompt=prompt, llm=OpenAI(), memory=memory)
    """

    def __init__(self, llm: LLM, max_buffer_rounds: int = 2) -> None:
        self.llm = llm
        self.max_buffer_rounds = max_buffer_rounds
        self._buffer: list[tuple[str, str]] = []
        self._summary: str = ""

        self._summary_chain = LLMChain(
            prompt=INITIAL_SUMMARY_PROMPT, llm=self.llm,
        )
        self._incremental_chain = LLMChain(
            prompt=INCREMENTAL_SUMMARY_PROMPT, llm=self.llm,
        )

    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]) -> None:
        """Save one round and trigger summarization if buffer is full.

        Args:
            inputs: The input variables dict (e.g. {"question": "hi"}).
            outputs: The output dict (e.g. {"text": "hello"}).
        """
        human_msg = " ".join(f"{v}" for v in inputs.values())
        ai_msg = " ".join(f"{v}" for v in outputs.values())
        self._buffer.append((human_msg, ai_msg))

        # Trigger summarization when buffer exceeds max_buffer_rounds
        if len(self._buffer) > self.max_buffer_rounds:
            self._compress_buffer()

    def _compress_buffer(self) -> None:
        """Compress all buffered rounds into the summary."""
        new_exchanges = self._format_buffer()

        if self._summary:
            # Incremental: update existing summary with new exchanges
            self._summary = self._incremental_chain.run(
                summary=self._summary,
                new_exchanges=new_exchanges,
            )
        else:
            # First time: generate initial summary from buffer
            self._summary = self._summary_chain.run(
                conversation=new_exchanges,
            )

        self._buffer.clear()

    def _format_buffer(self) -> str:
        """Format buffer entries as alternating Human/AI lines."""
        lines = []
        for human, ai in self._buffer:
            lines.append(f"Human: {human}")
            lines.append(f"AI: {ai}")
        return "\n".join(lines)

    def load_context(self) -> str:
        """Return summary plus recent buffer as formatted history.

        Returns:
            The summary of older rounds followed by the recent
            un-summarized rounds. Empty string if no history.
        """
        parts = []
        if self._summary:
            parts.append(self._summary)
        if self._buffer:
            parts.append(self._format_buffer())
        return "\n".join(parts)

    def clear(self) -> None:
        """Reset summary and buffer."""
        self._summary = ""
        self._buffer.clear()