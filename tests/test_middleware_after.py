"""Tests for after_llm and after_tool middleware hooks."""

from langchain.agents.middleware import Middleware


class RecordingMiddleware(Middleware):
    """Records all hook calls for verification."""
    def __init__(self):
        self.calls = []
    def after_llm(self, messages, response):
        self.calls.append(("after_llm", response))
        return response.upper()
    def after_tool(self, tool_name, tool_input, result):
        self.calls.append(("after_tool", result))
        return f"[{result}]"


def test_after_llm_called_and_transforms():
    mw = RecordingMiddleware()
    result = mw.after_llm(["msg1"], "hello")
    assert result == "HELLO"
    assert ("after_llm", "hello") in mw.calls


def test_after_tool_called_and_transforms():
    mw = RecordingMiddleware()
    result = mw.after_tool("calc", "2+3", "5")
    assert result == "[5]"
    assert ("after_tool", "5") in mw.calls


def test_default_after_llm_passes_through():
    mw = Middleware()
    assert mw.after_llm(["m"], "x") == "x"


def test_default_after_tool_passes_through():
    mw = Middleware()
    assert mw.after_tool("t", "i", "r") == "r"


def test_multiple_middleware_chain_after():
    """after_tool chaining: each middleware transforms the result."""
    class AppendA(Middleware):
        def after_tool(self, n, i, r): return r + "A"
    class AppendB(Middleware):
        def after_tool(self, n, i, r): return r + "B"

    result = "X"
    for mw in [AppendA(), AppendB()]:
        result = mw.after_tool("t", "i", result)
    assert result == "XAB"


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
