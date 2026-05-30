"""Tests for Memory ↔ Chat Model bridge via load_messages()."""

from langchain.memory.buffer import ConversationBufferMemory
from langchain.memory.buffer_window import ConversationBufferWindowMemory
from langchain.memory.summary import ConversationSummaryMemory
from langchain.llms.base import LLM
from langchain.schema import HumanMessage, AIMessage, BaseMessage


class FakeLLM(LLM):
    """LLM that returns canned summaries."""
    def __init__(self, responses=None):
        self.responses = responses or []
        self._idx = 0
    def _generate(self, prompts):
        r = self.responses[self._idx] if self._idx < len(self.responses) else "summary"
        self._idx += 1
        return [r]


# ── ConversationBufferMemory ────────────────────────────────────
def test_buffer_load_messages_empty():
    mem = ConversationBufferMemory()
    assert mem.load_messages() == []


def test_buffer_load_messages_one_turn():
    mem = ConversationBufferMemory()
    mem.save_context({"question": "hi"}, {"text": "hello"})
    msgs = mem.load_messages()
    assert len(msgs) == 2
    assert isinstance(msgs[0], HumanMessage)
    assert msgs[0].content == "hi"
    assert isinstance(msgs[1], AIMessage)
    assert msgs[1].content == "hello"


def test_buffer_load_messages_two_turns():
    mem = ConversationBufferMemory()
    mem.save_context({"question": "hi"}, {"text": "hello"})
    mem.save_context({"question": "bye"}, {"text": "goodbye"})
    msgs = mem.load_messages()
    assert len(msgs) == 4
    assert msgs[0].content == "hi"
    assert msgs[1].content == "hello"
    assert msgs[2].content == "bye"
    assert msgs[3].content == "goodbye"


def test_buffer_load_context_still_works():
    """load_context() must still return a string."""
    mem = ConversationBufferMemory()
    mem.save_context({"question": "hi"}, {"text": "hello"})
    ctx = mem.load_context()
    assert isinstance(ctx, str)
    assert "Human: hi" in ctx
    assert "AI: hello" in ctx


# ── ConversationBufferWindowMemory ──────────────────────────────
def test_window_load_messages_respects_k():
    mem = ConversationBufferWindowMemory(k=1)
    mem.save_context({"q": "a"}, {"t": "A"})
    mem.save_context({"q": "b"}, {"t": "B"})
    msgs = mem.load_messages()
    assert len(msgs) == 2  # only last turn
    assert msgs[0].content == "b"
    assert msgs[1].content == "B"


def test_window_load_messages_k_larger_than_buffer():
    mem = ConversationBufferWindowMemory(k=10)
    mem.save_context({"q": "a"}, {"t": "A"})
    msgs = mem.load_messages()
    assert len(msgs) == 2  # all available


# ── ConversationSummaryMemory ──────────────────────────────────
def test_summary_load_messages_with_summary():
    mem = ConversationSummaryMemory(llm=FakeLLM(responses=["User asked about Python"]))
    mem.save_context({"q": "What is Python?"}, {"t": "A programming language"})
    mem.save_context({"q": "Tell me more"}, {"t": "Python is versatile"})
    mem.save_context({"q": "Ok"}, {"t": "Great!"})  # triggers compression

    msgs = mem.load_messages()

    # Should have: summary HumanMessage + recent buffer HumanMessage + AIMessage
    assert len(msgs) >= 1
    assert isinstance(msgs[0], HumanMessage)
    # The summary message should contain the compressed summary
    assert "Summary" in msgs[0].content or "Python" in msgs[0].content


def test_summary_load_messages_empty():
    mem = ConversationSummaryMemory(llm=FakeLLM())
    assert mem.load_messages() == []


if __name__ == "__main__":
    import sys
    functions = [n for n in dir() if n.startswith("test_")]
    passed = 0
    failed = 0
    for fn in sorted(functions):
        try:
            globals()[fn]()
            print(f"  ✓ {fn}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {fn}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
