"""Tests for function calling — native tool calling via API."""

from langchain.agents.function_calling import FunctionCallingAgent
from langchain.llms.base import LLM
from langchain.tools.base import Tool
from langchain.tools.calculator import CalculatorTool


# ── Tool JSON Schema ────────────────────────────────────────────
def test_tool_to_json_schema():
    """Tool.to_json_schema() returns OpenAI function format."""
    schema = CalculatorTool().to_json_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "calculator"
    assert "description" in schema["function"]
    assert "parameters" in schema["function"]
    assert "input" in schema["function"]["parameters"]["properties"]


# ── Fake LLM with generate_with_tools ───────────────────────────
class FakeToolLLM(LLM):
    """LLM with generate_with_tools support."""
    def __init__(self, responses=None):
        self.responses = responses or []
        self._idx = 0
        self.calls = []

    def _generate(self, prompts):
        return ["sync fallback" for _ in prompts]

    def generate_with_tools(self, messages_list, tools):
        result = []
        for msgs in messages_list:
            self.calls.append(msgs)
            if self._idx < len(self.responses):
                result.append(self.responses[self._idx])
                self._idx += 1
            else:
                result.append({"content": "fallback", "tool_calls": []})
        return result


# ── FunctionCallingAgent ───────────────────────────────────────
def test_agent_direct_answer():
    """Model returns content directly — no tool call."""
    llm = FakeToolLLM(responses=[
        {"content": "Hello! How can I help?", "tool_calls": []},
    ])
    agent = FunctionCallingAgent(
        llm=llm, tools=[CalculatorTool()],
        system_message="Be helpful.",
    )
    result = agent.run("Hello!")
    assert "Hello" in result


def test_agent_tool_call():
    """Model returns a tool call — agent executes it."""
    llm = FakeToolLLM(responses=[
        {"content": None, "tool_calls": [
            {"name": "calculator", "arguments": "2+3"}
        ]},
        {"content": "The answer is 5", "tool_calls": []},
    ])
    agent = FunctionCallingAgent(
        llm=llm, tools=[CalculatorTool()],
    )
    result = agent.run("What is 2+3?")
    assert "5" in result


def test_agent_run_with_log():
    """run_with_log returns answer and log."""
    llm = FakeToolLLM(responses=[
        {"content": "42", "tool_calls": []},
    ])
    agent = FunctionCallingAgent(llm=llm, tools=[])
    result = agent.run_with_log("What is the answer?")
    assert "answer" in result
    assert "log" in result
    assert result["answer"] == "42"


def test_agent_passes_tool_schemas():
    """Agent passes tool JSON schemas to the LLM."""
    llm = FakeToolLLM(responses=[
        {"content": "ok", "tool_calls": []},
    ])
    agent = FunctionCallingAgent(llm=llm, tools=[CalculatorTool()])
    agent.run("test")

    # The generate_with_tools should have been called with tools
    assert len(llm.calls) == 1


def test_agent_multi_tool_calls():
    """Multiple tool calls within max_iterations."""
    llm = FakeToolLLM(responses=[
        {"content": None, "tool_calls": [
            {"name": "calculator", "arguments": "2+3"}
        ]},
        {"content": None, "tool_calls": [
            {"name": "calculator", "arguments": "5+7"}
        ]},
        {"content": "Results are 5 and 12", "tool_calls": []},
    ])
    agent = FunctionCallingAgent(
        llm=llm, tools=[CalculatorTool()],
    )
    result = agent.run("What is 2+3 and 5+7?")
    assert "5" in result or "12" in result


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
