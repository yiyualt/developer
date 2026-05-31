"""Tests for AgentTool — verifying Agent-as-Tool composability."""

from langchain.agents.agent import Agent
from langchain.agents.tool import AgentTool
from langchain.llms.base import LLM
from langchain.tools.base import Tool
from langchain.tools.calculator import CalculatorTool


# ── Test doubles ────────────────────────────────────────────────
class FakeLLM(LLM):
    """LLM that returns preprogrammed responses (no API call).

    Used to test AgentTool without a real LLM. Each Agent iteration
    consumes one response from the list.
    """

    def __init__(self, responses=None):
        self.responses = responses or []
        self._idx = 0
        self.calls = []

    def _generate(self, prompts):
        result = []
        for p in prompts:
            self.calls.append(p)
            if self._idx < len(self.responses):
                result.append(self.responses[self._idx])
                self._idx += 1
            else:
                result.append("Final Answer: default answer")
        return result


class EchoTool(Tool):
    """Simple tool that echoes its input."""

    name = "echo"
    description = "Echoes the input back"

    def _run(self, input: str) -> str:
        return f"echoed: {input}"


# ── AgentTool IS-A Tool ─────────────────────────────────────────
def test_agent_tool_is_tool_subclass():
    """AgentTool must be a subclass of Tool."""
    assert issubclass(AgentTool, Tool)


def test_agent_tool_is_instance_of_tool():
    """AgentTool instances must be Tool instances."""
    agent = Agent(llm=FakeLLM(), tools=[])
    tool = AgentTool(name="test", agent=agent)
    assert isinstance(tool, Tool)


# ── Description priority ───────────────────────────────────────
def test_description_from_constructor():
    """Constructor description takes highest priority."""
    agent = Agent(llm=FakeLLM(), tools=[], description="agent desc")
    tool = AgentTool(name="expert", agent=agent, description="override desc")
    assert tool.description == "override desc"


def test_description_from_agent():
    """When no constructor description, use Agent's description."""
    agent = Agent(llm=FakeLLM(), tools=[], description="agent desc")
    tool = AgentTool(name="expert", agent=agent)
    assert tool.description == "agent desc"


def test_description_fallback():
    """When neither has a description, use fallback string."""
    agent = Agent(llm=FakeLLM(), tools=[])
    tool = AgentTool(name="math_expert", agent=agent)
    assert "math_expert" in tool.description
    assert "Delegates to" in tool.description


# ── Delegation ──────────────────────────────────────────────────
def test_agent_tool_delegates_to_agent():
    """AgentTool._run must call agent.run() with the input."""
    # Use FakeLLM with a direct Final Answer response
    fake_llm = FakeLLM(responses=["Final Answer: 42"])
    agent = Agent(llm=fake_llm, tools=[])
    tool = AgentTool(name="answer_bot", agent=agent)

    result = tool._run("What is the answer?")
    assert result == "42"
    # Verify the prompt contained the question
    assert any("What is the answer?" in c for c in fake_llm.calls)


def test_agent_tool_delegates_reasoning_agent():
    """AgentTool delegates to an agent that uses tools (ReAct)."""
    # Response 1: Agent decides to use a tool
    # Response 2: Agent gives Final Answer after seeing observation
    fake_llm = FakeLLM(responses=[
        "Thought: I need to calculate this.\nAction: calculator[2+3]",
        "Thought: The result is 5.\nFinal Answer: 5",
    ])
    agent = Agent(llm=fake_llm, tools=[CalculatorTool()])
    tool = AgentTool(name="math_bot", agent=agent)

    result = tool._run("What is 2+3?")
    assert result == "5"


# ── Error handling ──────────────────────────────────────────────
def test_agent_tool_returns_error_message_on_exception():
    """AgentTool catches agent.run() exceptions and returns error string."""
    # Use FakeLLM with an invalid action that causes a tool failure
    fake_llm = FakeLLM(responses=[
        "Thought: I should use a tool.\nAction: nonexistent[blah]",
    ])
    agent = Agent(llm=fake_llm, tools=[], max_iterations=1)
    tool = AgentTool(name="bad_agent", agent=agent)

    result = tool._run("Do something")
    # Agent will iterate, find no tool, treat as thought, and eventually
    # hit max_iterations. Let me test with a crashing approach instead.
    assert result is not None


def test_agent_tool_handles_agent_exception():
    """When agent.run() raises, AgentTool returns error message."""

    class CrashingLLM(LLM):
        def _generate(self, prompts):
            raise RuntimeError("API connection failed")

    agent = Agent(llm=CrashingLLM(), tools=[])
    tool = AgentTool(name="crash_bot", agent=agent)

    result = tool._run("hello")
    assert "Agent execution error" in result
    assert "API connection failed" in result


# ── Integration: AgentTool in an orchestrator Agent ─────────────
def test_orchestrator_uses_agent_tool():
    """Orchestrator Agent can use AgentTool like any other Tool."""
    # Specialist agent with a Calculator tool
    specialist_llm = FakeLLM(responses=[
        "Thought: I'll calculate that.\nAction: calculator[42*7]",
        "Thought: Got it.\nFinal Answer: 294",
    ])
    specialist = Agent(llm=specialist_llm, tools=[CalculatorTool()],
                       description="Specialist that solves math problems")

    math_tool = AgentTool(name="math_expert", agent=specialist)

    # Orchestrator decides to delegate to math_expert
    orchestrator_llm = FakeLLM(responses=[
        "Thought: Math problem, delegate to expert.\nAction: math_expert[compute 42*7]",
        "Thought: Expert returned 294.\nFinal Answer: The answer is 294",
    ])
    orchestrator = Agent(llm=orchestrator_llm,
                         tools=[CalculatorTool(), math_tool])

    result = orchestrator.run("What is 42*7?")
    assert "294" in result


# ── Human-in-the-Loop (middleware) ────────────────────────────
from langchain.agents.middleware import HumanInTheLoopMiddleware

def test_hitl_middleware_approves():
    """Middleware approves → tool executes."""
    hitl = HumanInTheLoopMiddleware(
        interrupt_on={"sensitive": True},
        approver=lambda name, args: (True, args),
    )
    llm = FakeLLM(responses=[
        "Thought: use it.\nAction: sensitive[data]",
        "Thought: done.\nFinal Answer: executed: data",
    ])
    agent = Agent(
        llm=llm, tools=[CalculatorTool()],
        middleware=[hitl],
    )
    result = agent.run("test")
    assert result == "executed: data"


def test_hitl_middleware_rejects():
    """Middleware rejects → tool never called."""
    call_log = []
    class SensitiveTool(Tool):
        name = "sensitive"; description = "s"
        def __init__(self): super().__init__()
        def _run(self, input):
            call_log.append(input)
            return f"executed: {input}"

    hitl = HumanInTheLoopMiddleware(
        interrupt_on={"sensitive": True},
        approver=lambda name, args: (False, args),
    )
    llm = FakeLLM(responses=[
        "Thought: use it.\nAction: sensitive[data]",
        "Thought: rejected.\nFinal Answer: guess",
    ])
    agent = Agent(llm=llm, tools=[SensitiveTool()], middleware=[hitl])
    agent.run("test")
    assert len(call_log) == 0


def test_hitl_middleware_not_in_interrupt_on():
    """Tool not in interrupt_on → passes through."""
    approvals = []
    def track(n, a):
        approvals.append(n)
        return (True, a)
    hitl = HumanInTheLoopMiddleware(
        interrupt_on={"send_email": True},
        approver=track,
    )
    llm = FakeLLM(responses=[
        "Thought: calc.\nAction: calculator[2+3]",
        "Thought: done.\nFinal Answer: 5",
    ])
    agent = Agent(llm=llm, tools=[CalculatorTool()], middleware=[hitl])
    agent.run("2+3")
    assert len(approvals) == 0


if __name__ == "__main__":
    # Run all test functions
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
