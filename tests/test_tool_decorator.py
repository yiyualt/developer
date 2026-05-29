"""Tests for @tool decorator — function → Tool conversion."""

from langchain.tools.base import Tool
from langchain.tools.decorator import tool


# ── Basic decoration ────────────────────────────────────────────
def test_basic_decorator_creates_tool_instance():
    """@tool on a function returns a Tool instance."""
    @tool
    def greet(input: str) -> str:
        """Greets a person."""
        return f"Hello, {input}"

    assert isinstance(greet, Tool)


def test_name_from_function_name():
    """Tool name comes from function name."""
    @tool
    def greet(input: str) -> str:
        """Greets a person."""
        return f"Hello, {input}"

    assert greet.name == "greet"


def test_description_from_docstring():
    """Tool description comes from docstring first line."""
    @tool
    def greet(input: str) -> str:
        """Greets a person warmly."""
        return f"Hello, {input}"

    assert greet.description == "Greets a person warmly."


def test_run_delegates_to_function():
    """run() calls the decorated function body."""
    @tool
    def greet(input: str) -> str:
        """Greets a person."""
        return f"Hello, {input}"

    result = greet.run("World")
    assert result == "Hello, World"


# ── Explicit name/description ───────────────────────────────────
def test_explicit_name():
    """@tool(name=...) overrides function name."""
    @tool(name="calculator")
    def calc(input: str) -> str:
        """Does math."""
        return str(eval(input))

    assert calc.name == "calculator"


def test_explicit_description():
    """@tool(description=...) overrides docstring."""
    @tool(description="Performs arithmetic")
    def calc(input: str) -> str:
        """Docstring ignored."""
        return str(eval(input))

    assert calc.description == "Performs arithmetic"


def test_explicit_name_and_description():
    """@tool(name=..., description=...) overrides both."""
    @tool(name="calc", description="Solves math problems")
    def calculator(input: str) -> str:
        """Original description."""
        return str(eval(input))

    assert calculator.name == "calc"
    assert calculator.description == "Solves math problems"
    assert calculator.run("2+3") == "5"


# ── Docstring handling ──────────────────────────────────────────
def test_multiline_docstring_uses_first_line():
    """Multi-line docstring: only first line used as description."""
    @tool
    def helper(input: str) -> str:
        """First line only.

        This second line is ignored.
        And this third line too.
        """
        return input

    assert helper.description == "First line only."


def test_no_docstring():
    """Function without docstring: description is empty string."""
    @tool
    def helper(input: str) -> str:
        return input

    assert helper.description == ""


# ── Integration: tool works with Agent ──────────────────────────
def test_tool_works_in_agent():
    """Decorated tool can be used in Agent's tools list."""
    from langchain.agents.agent import Agent
    from langchain.llms.base import LLM

    @tool
    def echo(input: str) -> str:
        """Echoes the input back."""
        return f"ECHO: {input}"

    # FakeLLM: returns one response per prompt
    class FakeLLM(LLM):
        def __init__(self, responses=None):
            self.responses = responses or []
            self._idx = 0

        def _generate(self, prompts):
            result = []
            for _ in prompts:
                if self._idx < len(self.responses):
                    result.append(self.responses[self._idx])
                    self._idx += 1
                else:
                    result.append("Final Answer: fallback")
            return result

    fake_llm = FakeLLM(responses=[
        "Thought: I'll echo.\nAction: echo[hello]",
        "Thought: Got result.\nFinal Answer: ECHO: hello",
    ])

    agent = Agent(llm=fake_llm, tools=[echo])
    result = agent.run(question="Echo hello")
    assert "ECHO" in result


if __name__ == "__main__":
    import sys

    functions = [name for name in dir() if name.startswith("test_")]
    passed = 0
    failed = 0

    for func_name in sorted(functions):
        func = globals()[func_name]
        try:
            func()
            print(f"  ✓ {func_name}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {func_name}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
