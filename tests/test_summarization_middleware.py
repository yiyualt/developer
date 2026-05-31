"""Tests for SummarizationMiddleware — context compression."""

from langchain.agents.middleware import SummarizationMiddleware
from langchain.llms.base import LLM
from langchain.schema import HumanMessage, SystemMessage, AIMessage


class FakeLLM(LLM):
    def __init__(self, responses=None):
        self.responses = responses or []
        self._idx = 0
    def _generate(self, prompts):
        r = [self.responses[self._idx]] if self._idx < len(self.responses) else ["ok"]
        self._idx += 1
        return r


# ── before_llm ────────────────────────────────────────────────
def test_below_threshold_no_change():
    """Messages under limit pass through unchanged."""
    llm = FakeLLM(responses=["unused"])
    mw = SummarizationMiddleware(llm=llm, max_tokens=4000, keep_recent=3)

    msgs = [HumanMessage("short")]
    result = mw.before_llm(msgs)
    assert result == msgs


def test_above_threshold_summarizes():
    """Messages over limit → older ones replaced with summary."""
    llm = FakeLLM(responses=["compressed summary"])
    mw = SummarizationMiddleware(llm=llm, max_tokens=1, keep_recent=1)

    msgs = [
        HumanMessage("long message here"),
        AIMessage("another long message"),
        HumanMessage("most recent message"),
    ]
    result = mw.before_llm(msgs)

    assert len(result) == 2  # summary + 1 kept recent
    assert "compressed summary" in result[0].content
    assert result[1].content == "most recent message"


def test_keep_recent_unchanged():
    """keep_recent messages are preserved unmodified."""
    llm = FakeLLM(responses=["summary"])
    mw = SummarizationMiddleware(llm=llm, max_tokens=1, keep_recent=2)

    msgs = [
        SystemMessage("sys"),
        HumanMessage("old1"),
        AIMessage("old2"),
        HumanMessage("latest"),
        AIMessage("newest"),
    ]
    result = mw.before_llm(msgs)
    # keep_recent=2 → last 2 messages kept, first 3 summarized
    assert result[-1].content == "newest"
    assert result[-2].content == "latest"


def test_few_messages_than_keep_recent_no_summary():
    """If total messages ≤ keep_recent, nothing happens."""
    llm = FakeLLM(responses=["unused"])
    mw = SummarizationMiddleware(llm=llm, max_tokens=1, keep_recent=5)

    msgs = [HumanMessage("hi")]
    result = mw.before_llm(msgs)
    # Even though over token limit, keep_recent keeps all
    assert result == msgs


if __name__ == "__main__":
    import sys
    fns = [n for n in dir() if n.startswith("test_")]
    p = f = 0
    for fn in sorted(fns):
        try:
            globals()[fn]()
            print(f"  ✓ {fn}")
            p += 1
        except Exception as e:
            print(f"  ✗ {fn}: {e}")
            f += 1
    print(f"\n{p} passed, {f} failed")
    sys.exit(1 if f else 0)
