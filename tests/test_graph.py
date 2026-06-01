"""Tests for LangGraph v0.0.1 — StateGraph with Channels and Reducers."""

from langgraph import StateGraph
from langgraph.channels import append


class State:
    messages: list  # default: replace


class AppendState:
    # Use Annotated for append reducer
    from typing import Annotated
    messages: Annotated[list, append]


# ── Basic graph ─────────────────────────────────────────────────
def test_simple_linear_graph():
    graph = StateGraph(State)
    graph.add_node("greet", lambda s: {"messages": ["Hello"]})
    graph.add_edge("__start__", "greet")
    graph.add_edge("greet", "__end__")

    result = graph.compile().invoke({"messages": []})
    assert result["messages"] == ["Hello"]


def test_two_nodes():
    graph = StateGraph(State)
    graph.add_node("a", lambda s: {"messages": ["A"]})
    graph.add_node("b", lambda s: {"messages": ["B"]})
    graph.add_edge("__start__", "a")
    graph.add_edge("a", "b")
    graph.add_edge("b", "__end__")

    result = graph.compile().invoke({"messages": []})
    # replace reducer: "b" overwrites "a"
    assert result["messages"] == ["B"]


# ── Append reducer ──────────────────────────────────────────────
def test_append_reducer_accumulates():
    """append channel: both node outputs accumulated."""
    class TestState:
        from typing import Annotated
        messages: Annotated[list, append]

    graph = StateGraph(TestState)
    graph.add_node("a", lambda s: {"messages": ["A"]})
    graph.add_node("b", lambda s: {"messages": ["B"]})
    graph.add_edge("__start__", "a")
    graph.add_edge("a", "b")
    graph.add_edge("b", "__end__")

    result = graph.compile().invoke({"messages": []})
    assert result["messages"] == ["A", "B"]


def test_append_with_initial_value():
    """append channel: initial list + node output."""
    class TestState:
        from typing import Annotated
        messages: Annotated[list, append]

    graph = StateGraph(TestState)
    graph.add_node("a", lambda s: {"messages": ["hello"]})
    graph.add_edge("__start__", "a")
    graph.add_edge("a", "__end__")

    result = graph.compile().invoke({"messages": ["existing"]})
    assert result["messages"] == ["existing", "hello"]


# ── Multiple fields ─────────────────────────────────────────────
def test_multiple_fields():
    """Multiple state fields with different reducers."""
    class TestState:
        from typing import Annotated
        messages: Annotated[list, append]
        name: str  # default replace

    graph = StateGraph(TestState)
    graph.add_node("a", lambda s: {"messages": ["A"], "name": "Alice"})
    graph.add_node("b", lambda s: {"messages": ["B"], "name": "Bob"})
    graph.add_edge("__start__", "a")
    graph.add_edge("a", "b")
    graph.add_edge("b", "__end__")

    result = graph.compile().invoke({"messages": [], "name": ""})
    assert result["messages"] == ["A", "B"]  # append
    assert result["name"] == "Bob"           # replace


# ── Default schema (dict) ───────────────────────────────────────
def test_default_schema():
    """StateGraph(dict): bare dict, all fields are replace."""
    graph = StateGraph(dict)
    graph.add_node("a", lambda s: {"x": 1, "y": 2})
    graph.add_node("b", lambda s: {"y": 99})
    graph.add_edge("__start__", "a")
    graph.add_edge("a", "b")
    graph.add_edge("b", "__end__")

    result = graph.compile().invoke({"x": 0})
    assert result["x"] == 1   # from "a"
    assert result["y"] == 99  # "b" overwrote "a"


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
