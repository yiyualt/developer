"""Tests for callback consistency — all components accept callbacks."""

from langchain.agents.agent import Agent
from langchain.agents.orchestrator import MultiAgentOrchestrator, SequentialAgentChain
from langchain.agents.plan_execute import PlanAndExecuteAgent
from langchain.agents.self_correct import LLMCorrector, SelfCorrectingAgent
from langchain.agents.tool import AgentTool
from langchain.callbacks.base import CallbackHandler
from langchain.callbacks.stdout import StdOutCallbackHandler
from langchain.chains.llm_chain import LLMChain
from langchain.llms.base import LLM
from langchain.prompts.prompt import PromptTemplate
from langchain.tools.base import Tool


class FakeLLM(LLM):
    def __init__(self, responses=None):
        self.responses = responses or []
        self._idx = 0
    def _generate(self, prompts):
        r = [self.responses[self._idx]] if self._idx < len(self.responses) else ["fallback"]
        self._idx += 1
        return r


class RecordingHandler(CallbackHandler):
    """Records all events for verification."""
    def __init__(self):
        self.events = []
    def on_llm_start(self, **kw): self.events.append(("on_llm_start", kw))
    def on_llm_end(self, **kw): self.events.append(("on_llm_end", kw))
    def on_chain_start(self, **kw): self.events.append(("on_chain_start", kw))
    def on_chain_end(self, **kw): self.events.append(("on_chain_end", kw))
    def on_tool_start(self, **kw): self.events.append(("on_tool_start", kw))
    def on_tool_end(self, **kw): self.events.append(("on_tool_end", kw))
    def on_agent_action(self, **kw): self.events.append(("on_agent_action", kw))
    def on_agent_finish(self, **kw): self.events.append(("on_agent_finish", kw))
    def on_error(self, **kw): self.events.append(("on_error", kw))
    def on_llm_new_token(self, **kw): self.events.append(("on_llm_new_token", kw))


# ── Agent: no duplicate tool events ─────────────────────────────
def test_agent_no_duplicate_tool_fire():
    """Tool.run fires on_tool_start/end once, not from Agent layer."""
    handler = RecordingHandler()

    agent_llm = FakeLLM(responses=[
        "Thought: I should search.\nAction: search[test]",
        "Thought: Got it.\nFinal Answer: done",
    ])
    class SearchTool(Tool):
        name = "search"
        description = "searches"
        def __init__(self, callbacks=None):
            super().__init__(callbacks=callbacks)
        def _run(self, input): return "result"
    search = SearchTool(callbacks=[handler])

    agent = Agent(llm=agent_llm, tools=[search], callbacks=[handler])
    agent.run("test")

    tool_starts = [e for e in handler.events if e[0] == "on_tool_start"]
    tool_ends = [e for e in handler.events if e[0] == "on_tool_end"]
    # Should fire exactly once (from Tool.run, not Agent._execute_tool)
    assert len(tool_starts) == 1, f"Expected 1 on_tool_start, got {len(tool_starts)}"
    assert len(tool_ends) == 1, f"Expected 1 on_tool_end, got {len(tool_ends)}"


# ── AgentTool accepts callbacks ─────────────────────────────────
def test_agent_tool_accepts_callbacks():
    """AgentTool merges callbacks into wrapped Agent."""
    handler = RecordingHandler()

    inner_llm = FakeLLM(responses=["Final Answer: hello from inner"])

    inner = Agent(llm=inner_llm, tools=[], description="inner")
    tool = AgentTool(name="test", agent=inner, callbacks=[handler])
    tool.run("hi")

    # The inner agent's callbacks should include our handler
    assert handler in inner.callbacks


# ── PlanAndExecuteAgent accepts callbacks ───────────────────────
def test_plan_execute_accepts_callbacks():
    """PlanAndExecuteAgent has callbacks attribute."""
    handler = RecordingHandler()
    agent = PlanAndExecuteAgent(
        llm=FakeLLM(responses=["1. Step one", "done"]),
        callbacks=[handler],
    )
    assert handler in agent.callbacks


# ── Orchestrator accepts callbacks ──────────────────────────────
def test_orchestrator_accepts_callbacks():
    """MultiAgentOrchestrator passes callbacks to internal Agent."""
    handler = RecordingHandler()
    specialist = Agent(llm=FakeLLM(responses=["Final Answer: ok"]), tools=[])
    orch_llm = FakeLLM(responses=[
        "Thought: delegate.\nAction: specialist_0[hi]",
        "Thought: done.\nFinal Answer: ok",
    ])
    orch = MultiAgentOrchestrator(
        llm=orch_llm,
        specialists=[specialist],
        callbacks=[handler],
    )
    # _orchestrator should have the callbacks
    assert handler in orch._orchestrator.callbacks


# ── SequentialAgentChain accepts callbacks ──────────────────────
def test_sequential_chain_accepts_callbacks():
    """SequentialAgentChain merges callbacks into agents."""
    handler = RecordingHandler()
    a1 = Agent(llm=FakeLLM(responses=["Final Answer: step1"]), tools=[])
    a2 = Agent(llm=FakeLLM(responses=["Final Answer: step2"]), tools=[])

    chain = SequentialAgentChain(agents=[a1, a2], callbacks=[handler])
    assert handler in a1.callbacks
    assert handler in a2.callbacks


# ── SelfCorrectingAgent + LLMCorrector accept callbacks ─────────
def test_self_correct_accepts_callbacks():
    """SelfCorrectingAgent merges callbacks into wrapped agent."""
    handler = RecordingHandler()
    inner = Agent(llm=FakeLLM(responses=["Final Answer: 4"]), tools=[])
    corrector = LLMCorrector(
        llm=FakeLLM(responses=["PASS"]),
        callbacks=[handler],
    )
    sc = SelfCorrectingAgent(agent=inner, corrector=corrector, callbacks=[handler])

    assert handler in inner.callbacks
    assert handler in sc.callbacks


# ── LLMChain still works ────────────────────────────────────────
def test_llm_chain_callbacks_still_work():
    """LLMChain inherited CallbackMixin — should fire events."""
    handler = RecordingHandler()
    llm = FakeLLM(responses=["Python is a language"])
    prompt = PromptTemplate("Tell me about {topic}")
    chain = LLMChain(prompt=prompt, llm=llm, callbacks=[handler])
    chain.run(topic="Python")

    # Should have chain and LLM events
    event_names = [e[0] for e in handler.events]
    assert "on_chain_start" in event_names
    assert "on_llm_start" in event_names


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
