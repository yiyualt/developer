"""Tests for PlanAndExecuteAgent — plan decomposition and step execution."""

from langchain.agents.plan_execute import PlanAndExecuteAgent
from langchain.llms.base import LLM
from langchain.tools.base import Tool


# ── Test doubles ────────────────────────────────────────────────
class FakeLLM(LLM):
    """LLM that returns preprogrammed responses per call."""

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
                result.append("default response")
        return result


class EchoTool(Tool):
    """Simple tool that echoes input with a prefix."""

    name = "echo"
    description = "Echoes input back"

    def _run(self, input: str) -> str:
        return f"echoed: {input}"


# ── Plan parsing ────────────────────────────────────────────────
def test_parse_plan_dot_format():
    """Parse "1. Step" format."""
    agent = PlanAndExecuteAgent(llm=FakeLLM())
    plan = agent._parse_plan("1. Research the topic\n2. Write summary\n3. Review")
    assert plan == ["Research the topic", "Write summary", "Review"]


def test_parse_plan_paren_format():
    """Parse "1) Step" format."""
    agent = PlanAndExecuteAgent(llm=FakeLLM())
    plan = agent._parse_plan("1) First step\n2) Second step")
    assert plan == ["First step", "Second step"]


def test_parse_plan_mixed_format():
    """Parse mixed numbering formats."""
    agent = PlanAndExecuteAgent(llm=FakeLLM())
    plan = agent._parse_plan("1) Step A\n2. Step B\n3) Step C")
    assert plan == ["Step A", "Step B", "Step C"]


def test_parse_plan_ignores_non_numbered():
    """Non-numbered lines should be ignored."""
    agent = PlanAndExecuteAgent(llm=FakeLLM())
    plan = agent._parse_plan(
        "Here is my plan:\n1. Do X\n\n2. Do Y\nThis is a note."
    )
    assert plan == ["Do X", "Do Y"]


def test_parse_plan_empty_response():
    """Empty response returns empty plan."""
    agent = PlanAndExecuteAgent(llm=FakeLLM())
    plan = agent._parse_plan("")
    assert plan == []


# ── Plan generation ─────────────────────────────────────────────
def test_plan_generation():
    """LLM is called to generate a plan."""
    fake_llm = FakeLLM(responses=["1. Step one\n2. Step two"])
    agent = PlanAndExecuteAgent(llm=fake_llm)
    plan = agent._plan(goal="Test goal")
    assert plan == ["Step one", "Step two"]
    assert any("Test goal" in c for c in fake_llm.calls)


def test_plan_respects_max_steps():
    """Plan is truncated to max_steps."""
    fake_llm = FakeLLM(responses=[
        "1. A\n2. B\n3. C\n4. D\n5. E\n6. F\n7. G\n8. H"
    ])
    agent = PlanAndExecuteAgent(llm=fake_llm, max_steps=3)
    plan = agent._plan(goal="Do everything")
    assert len(plan) == 3
    assert plan == ["A", "B", "C"]


# ── Execution context ───────────────────────────────────────────
def test_execution_context_includes_goal_and_plan():
    """Context must contain the goal and full plan."""
    agent = PlanAndExecuteAgent(llm=FakeLLM())
    context = agent._build_execution_context(
        current_step="Do step 1",
        goal="Write a report",
        plan=["Do step 1", "Do step 2"],
        step_num=1,
        previous_results=[],
    )
    assert "Write a report" in context
    assert "Do step 1" in context
    assert "Do step 2" in context
    assert "CURRENT" in context


def test_execution_context_includes_previous_results():
    """Context must contain previous step results."""
    agent = PlanAndExecuteAgent(llm=FakeLLM())
    previous = [
        {"step_num": 1, "step": "Research", "result": "Found data: Python is popular"},
    ]
    context = agent._build_execution_context(
        current_step="Write report",
        goal="Analyze Python",
        plan=["Research", "Write report"],
        step_num=2,
        previous_results=previous,
    )
    assert "Found data: Python is popular" in context
    assert "Step 1" in context


# ── Step execution ──────────────────────────────────────────────
def test_execute_step_without_tools():
    """Without tools, step is executed via direct LLM call."""
    fake_llm = FakeLLM(responses=["Research completed: Python was created in 1991"])
    agent = PlanAndExecuteAgent(llm=fake_llm)
    result = agent._execute_step(
        step="Research Python history",
        goal="Write about Python",
        plan=["Research Python history", "Write summary"],
        step_num=1,
        previous_results=[],
    )
    assert "Python" in result


def test_execute_step_with_tools():
    """With tools, step execution creates an Agent with access to tools."""
    # The FakeLLM needs 2 responses: one for Agent's ReAct step,
    # one for Final Answer
    fake_llm = FakeLLM(responses=[
        "Thought: I'll use echo tool.\nAction: echo[hello world]",
        "Thought: Got echoed result.\nFinal Answer: echoed: hello world",
    ])
    agent = PlanAndExecuteAgent(llm=fake_llm, tools=[EchoTool()])
    result = agent._execute_step(
        step="Echo a message",
        goal="Test echo",
        plan=["Echo a message"],
        step_num=1,
        previous_results=[],
    )
    assert "echoed" in result.lower()


# ── run and run_with_log ────────────────────────────────────────
def test_run_returns_string():
    """run() returns the final answer as a string."""
    fake_llm = FakeLLM(responses=[
        # Plan
        "1. Say hello\n2. Say goodbye",
        # Step 1 execution
        "hello",
        # Step 2 execution
        "goodbye",
    ])
    agent = PlanAndExecuteAgent(llm=fake_llm)
    result = agent.run(goal="Say things")
    assert isinstance(result, str)
    assert "goodbye" in result


def test_run_with_log_returns_full_record():
    """run_with_log() returns plan, steps, and final_answer."""
    fake_llm = FakeLLM(responses=[
        # Plan
        "1. Step A\n2. Step B",
        # Step 1
        "result A",
        # Step 2
        "result B",
    ])
    agent = PlanAndExecuteAgent(llm=fake_llm)
    result = agent.run_with_log(goal="Test goal")

    assert "plan" in result
    assert "steps" in result
    assert "final_answer" in result
    assert len(result["plan"]) == 2
    assert len(result["steps"]) == 2
    assert result["steps"][0]["step"] == "Step A"
    assert result["steps"][0]["result"] == "result A"
    assert result["steps"][1]["result"] == "result B"
    assert result["final_answer"] == "result B"


# ── Integration: PlanAndExecuteAgent with AgentTool ─────────────
def test_plan_execute_with_agent_tool():
    """PlanAndExecuteAgent can use AgentTool in step execution."""
    from langchain.agents.agent import Agent
    from langchain.agents.tool import AgentTool

    # Specialist agent
    specialist_llm = FakeLLM(responses=[
        "Final Answer: 42",
    ])
    specialist = Agent(
        llm=specialist_llm,
        tools=[],
        description="Answers everything with 42",
    )

    math_tool = AgentTool(name="answer_bot", agent=specialist)

    # PlanAndExecuteAgent uses the specialist as a tool
    # Plan phase LLM response, then each step execution
    orchestrator_llm = FakeLLM(responses=[
        # Plan
        "1. Get the answer from the bot",
        # Step 1: Agent uses math_tool in ReAct
        "Thought: I need the answer.\nAction: answer_bot[What is the answer?]",
        "Thought: Got it.\nFinal Answer: 42",
    ])
    agent = PlanAndExecuteAgent(
        llm=orchestrator_llm,
        tools=[math_tool],
    )
    result = agent.run_with_log(goal="Find the ultimate answer")
    assert "42" in result["final_answer"]


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
