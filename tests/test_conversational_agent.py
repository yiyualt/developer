"""Tests for ConversationalAgent — message-native multi-turn dialogue."""

import asyncio

from langchain.agents.conversational import ConversationalAgent
from langchain.llms.base import LLM
from langchain.schema import HumanMessage, SystemMessage


class FakeMessageLLM(LLM):
    """LLM that supports both generate() and generate_messages()."""
    def __init__(self, responses=None):
        self.responses = responses or []
        self._idx = 0
        self.calls = []

    def _generate(self, prompts):
        return ["sync fallback" for _ in prompts]

    def generate_messages(self, messages_list):
        return self._do_generate(messages_list)

    async def agenerate_messages(self, messages_list):
        return self._do_generate(messages_list)

    def _do_generate(self, messages_list):
        result = []
        for msgs in messages_list:
            self.calls.append(msgs)
            if self._idx < len(self.responses):
                result.append(self.responses[self._idx])
                self._idx += 1
            else:
                result.append("Final Answer: fallback")
        return result


# ── Basic ───────────────────────────────────────────────────────
def test_conversational_agent_simple():
    """Single-turn question without tools."""
    llm = FakeMessageLLM(responses=["Final Answer: 4"])
    agent = ConversationalAgent(
        llm=llm, tools=[],
        system_message="You are helpful.",
    )
    assert agent.run("What is 2+2?") == "4"


def test_conversational_agent_sends_system_message():
    """SystemMessage is passed to generate_messages."""
    llm = FakeMessageLLM(responses=["Final Answer: ok"])
    agent = ConversationalAgent(
        llm=llm, tools=[],
        system_message="You are a math tutor.",
    )
    agent.run("test")

    # First message should be SystemMessage
    first_msg = llm.calls[0][0]
    assert isinstance(first_msg, SystemMessage)
    assert first_msg.content == "You are a math tutor."


def test_conversational_agent_sends_human_message():
    """HumanMessage with the question is included."""
    llm = FakeMessageLLM(responses=["Final Answer: ok"])
    agent = ConversationalAgent(llm=llm, tools=[])
    agent.run("What is Python?")

    # Find the HumanMessage with the question
    msgs = llm.calls[0]
    human_msgs = [m for m in msgs if isinstance(m, HumanMessage)]
    assert any("What is Python?" in m.content for m in human_msgs)


# ── Tool use ────────────────────────────────────────────────────
def test_conversational_agent_with_tool():
    """ReAct with tool use works."""
    from langchain.tools.calculator import CalculatorTool

    llm = FakeMessageLLM(responses=[
        "Thought: calculate.\nAction: calculator[2+3]",
        "Thought: got it.\nFinal Answer: 5",
    ])
    agent = ConversationalAgent(
        llm=llm, tools=[CalculatorTool()],
        system_message="You are helpful.",
    )
    result = agent.run("What is 2+3?")
    assert result == "5"


# ── Memory ──────────────────────────────────────────────────────
def test_conversational_agent_with_memory():
    """Memory stores and loads conversation history."""
    from langchain.memory.buffer import ConversationBufferMemory

    memory = ConversationBufferMemory()
    llm = FakeMessageLLM(responses=[
        "Final Answer: My name is Bot.",
        "Final Answer: Your name is User.",
    ])
    agent = ConversationalAgent(
        llm=llm, tools=[],
        system_message="You are helpful.",
        memory=memory,
    )

    # First turn — no history
    agent.run("What is your name?")
    # Second turn — should have history from first
    agent.run("What is my name?")

    # Memory should have 2 rounds
    ctx = memory.load_context()
    assert "Bot" in ctx
    assert "User" in ctx


# ── run_with_log ────────────────────────────────────────────────
def test_conversational_agent_run_with_log():
    """run_with_log returns answer and log."""
    llm = FakeMessageLLM(responses=["Final Answer: 42"])
    agent = ConversationalAgent(llm=llm, tools=[])
    result = agent.run_with_log("What is the answer?")
    assert "answer" in result
    assert "log" in result
    assert result["answer"] == "42"


# ── apply_async ─────────────────────────────────────────────────
def test_conversational_agent_apply_async():
    """apply_async runs multiple questions concurrently."""
    llm = FakeMessageLLM(responses=[
        "Final Answer: 4",
        "Final Answer: 6",
    ])
    agent = ConversationalAgent(llm=llm, tools=[])

    async def go():
        return await agent.apply_async(["Q1", "Q2"])

    results = asyncio.run(go())
    assert results == ["4", "6"]


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
