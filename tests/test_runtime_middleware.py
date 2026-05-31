"""Tests for Runtime middleware — call limits."""

from langchain.agents.middleware import (
    ModelCallLimitMiddleware, ToolCallLimitMiddleware,
)
from langchain.schema import HumanMessage, AIMessage


# ── ModelCallLimitMiddleware ──────────────────────────────────
def test_model_limit_under():
    mw = ModelCallLimitMiddleware(max_calls=3)
    msgs = [HumanMessage("hi")]
    for _ in range(3):
        assert mw.before_llm(msgs) == msgs


def test_model_limit_over():
    mw = ModelCallLimitMiddleware(max_calls=1)
    mw.before_llm([HumanMessage("hi")])  # count = 1
    result = mw.before_llm([HumanMessage("hi2")])  # count = 2
    assert len(result) == 1
    assert "limit exceeded" in result[0].content.lower()


def test_model_limit_resets_per_instance():
    mw1 = ModelCallLimitMiddleware(max_calls=2)
    mw2 = ModelCallLimitMiddleware(max_calls=2)
    mw1.before_llm([HumanMessage("a")])
    mw1.before_llm([HumanMessage("b")])
    # mw2 is independent
    assert mw2.before_llm([HumanMessage("x")]) == [HumanMessage("x")]


def test_model_limit_reset_clears_counter():
    """reset() clears the counter for a new Agent.run() call."""
    mw = ModelCallLimitMiddleware(max_calls=2)
    mw.before_llm([HumanMessage("a")])  # count=1
    mw.reset()
    mw.before_llm([HumanMessage("b")])  # count=1 again
    mw.before_llm([HumanMessage("c")])  # count=2 — still under limit
    # Reset again
    mw.reset()
    assert mw.before_llm([HumanMessage("d")]) == [HumanMessage("d")]


def test_tool_limit_reset_clears_counters():
    """reset() clears all per-tool and global counters."""
    mw = ToolCallLimitMiddleware(per_tool={"calc": 1})
    mw.before_tool("calc", "1")
    mw.reset()
    # After reset, calc should work again
    assert mw.before_tool("calc", "2") == (True, "2")


# ── ToolCallLimitMiddleware ───────────────────────────────────
def test_tool_limit_per_tool():
    mw = ToolCallLimitMiddleware(per_tool={"calc": 1})
    assert mw.before_tool("calc", "2+3") == (True, "2+3")
    # Second call exceeds limit
    proceed, msg = mw.before_tool("calc", "4+5")
    assert proceed is False
    assert "calc" in msg and "limit" in msg.lower()


def test_tool_limit_global():
    mw = ToolCallLimitMiddleware(max_calls=2)
    mw.before_tool("a", "1")
    mw.before_tool("b", "2")
    proceed, _ = mw.before_tool("c", "3")
    assert proceed is False


def test_tool_limit_unlisted_not_limited():
    mw = ToolCallLimitMiddleware(per_tool={"calc": 1})
    # search is not in per_tool — unlimited
    assert mw.before_tool("search", "python") == (True, "python")
    assert mw.before_tool("search", "rust") == (True, "rust")
    assert mw.before_tool("search", "go") == (True, "go")


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
