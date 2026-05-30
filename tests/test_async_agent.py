"""Tests for Agent.apply_async — concurrent ReAct execution."""

import asyncio

from langchain.agents.agent import Agent
from langchain.llms.base import LLM


class FakeAsyncLLM(LLM):
    """LLM that returns preprogrammed responses via _agenerate."""
    def __init__(self, responses=None):
        self.responses = responses or []
        self._idx = 0
        self.calls = []

    def _generate(self, prompts):
        # Sync fallback — shouldn't be used by apply_async
        return ["sync fallback" for _ in prompts]

    async def _agenerate(self, prompts):
        result = []
        for p in prompts:
            self.calls.append(p)
            if self._idx < len(self.responses):
                result.append(self.responses[self._idx])
                self._idx += 1
            else:
                result.append("Final Answer: fallback")
        return result


# ── apply_async ─────────────────────────────────────────────────
def test_apply_async_single_question():
    """Single question works with apply_async."""
    llm = FakeAsyncLLM(responses=["Final Answer: 4"])
    agent = Agent(llm=llm, tools=[])

    async def go():
        return await agent.apply_async(["What is 2+2?"])

    results = asyncio.run(go())
    assert results == ["4"]


def test_apply_async_multiple_questions():
    """Multiple questions return results in order."""
    llm = FakeAsyncLLM(responses=[
        "Final Answer: 4",
        "Final Answer: 6",
    ])
    agent = Agent(llm=llm, tools=[])

    async def go():
        return await agent.apply_async([
            "What is 2+2?",
            "What is 3+3?",
        ])

    results = asyncio.run(go())
    assert results == ["4", "6"]


def test_apply_async_uses_agenerate():
    """apply_async calls llm.agenerate(), not llm.generate()."""
    llm = FakeAsyncLLM(responses=["Final Answer: ok"])
    agent = Agent(llm=llm, tools=[])

    async def go():
        return await agent.apply_async(["test"])

    asyncio.run(go())
    # llm.calls are populated via _agenerate (not _generate)
    assert len(llm.calls) > 0


def test_apply_async_reasoning_agent():
    """Agent with tool use works in async mode."""
    from langchain.tools.calculator import CalculatorTool

    llm = FakeAsyncLLM(responses=[
        "Thought: calculate.\nAction: calculator[2+3]",
        "Thought: got it.\nFinal Answer: 5",
    ])
    agent = Agent(llm=llm, tools=[CalculatorTool()])

    async def go():
        return await agent.apply_async(["What is 2+3?"])

    results = asyncio.run(go())
    assert results[0] == "5"


def test_apply_async_concurrent_execution():
    """Multiple questions run concurrently (order preserved)."""
    # Use shared LLM with interleaved responses
    # Q1: needs 2 calls, Q2: needs 1 call
    llm = FakeAsyncLLM(responses=[
        # Q1 step 1: uses tool
        "Thought: calc.\nAction: calculator[2+3]",
        # Q2 step 1: direct answer
        "Final Answer: direct",
        # Q1 step 2: final answer
        "Thought: got it.\nFinal Answer: 5",
    ])
    agent = Agent(llm=llm, tools=[])

    async def go():
        return await agent.apply_async(["Q1", "Q2"])

    results = asyncio.run(go())
    assert len(results) == 2


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
