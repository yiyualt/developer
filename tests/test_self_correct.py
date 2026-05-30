"""Tests for SelfCorrectingAgent and LLMCorrector."""

from langchain.agents.agent import Agent
from langchain.agents.self_correct import LLMCorrector, SelfCorrectingAgent
from langchain.llms.base import LLM


class FakeLLM(LLM):
    """LLM that returns preprogrammed responses."""
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
                result.append("fallback")
        return result


# ── LLMCorrector ──────────────────────────────────────────────
def test_corrector_pass():
    """LLM responds PASS → check returns True."""
    llm = FakeLLM(responses=["PASS"])
    corrector = LLMCorrector(llm=llm)
    passed, feedback = corrector.check("What is 2+2?", "4")
    assert passed is True
    assert feedback == ""


def test_corrector_fail():
    """LLM responds with critique → check returns False."""
    llm = FakeLLM(responses=["The answer is wrong because it uses wrong formula"])
    corrector = LLMCorrector(llm=llm)
    passed, feedback = corrector.check("What is 2+2?", "5")
    assert passed is False
    assert "wrong" in feedback


def test_corrector_pass_case_insensitive():
    """PASS is case-insensitive."""
    llm = FakeLLM(responses=["pass"])
    corrector = LLMCorrector(llm=llm)
    passed, _ = corrector.check("q", "a")
    assert passed is True


# ── SelfCorrectingAgent ───────────────────────────────────────
def test_self_correct_passes_first_try():
    """Agent passes correction on first try — returns immediately."""
    agent_llm = FakeLLM(responses=["Final Answer: 4"])
    corrector_llm = FakeLLM(responses=["PASS"])

    agent = Agent(llm=agent_llm, tools=[])
    corrector = LLMCorrector(llm=corrector_llm)
    sc = SelfCorrectingAgent(agent, corrector)

    answer = sc.run("What is 2+2?")
    assert answer == "4"


def test_self_correct_retries_after_failure():
    """First answer fails, second passes — agent is called twice."""
    agent_llm = FakeLLM(responses=[
        "Final Answer: 5",    # first attempt — wrong
        "Final Answer: 4",    # retry — correct
    ])
    corrector_llm = FakeLLM(responses=[
        "Wrong! The answer should be 4.",  # fails first
        "PASS",                            # passes second
    ])

    agent = Agent(llm=agent_llm, tools=[])
    corrector = LLMCorrector(llm=corrector_llm)
    sc = SelfCorrectingAgent(agent, corrector)

    answer = sc.run("What is 2+2?")
    assert answer == "4"


def test_self_correct_max_retries_exhausted():
    """All attempts fail — returns last answer anyway."""
    agent_llm = FakeLLM(responses=[
        "Final Answer: 5",
        "Final Answer: 6",
        "Final Answer: 7",
    ])
    corrector_llm = FakeLLM(responses=[
        "Wrong!",
        "Still wrong!",
        "Wrong again!",
    ])

    agent = Agent(llm=agent_llm, tools=[])
    corrector = LLMCorrector(llm=corrector_llm)
    sc = SelfCorrectingAgent(agent, corrector, max_retries=3)

    answer = sc.run("What is 2+2?")
    assert answer == "7"  # last answer, even though all failed


def test_self_correct_run_with_log():
    """run_with_log returns attempts and final_answer."""
    agent_llm = FakeLLM(responses=["Final Answer: 4"])
    corrector_llm = FakeLLM(responses=["PASS"])

    agent = Agent(llm=agent_llm, tools=[])
    corrector = LLMCorrector(llm=corrector_llm)
    sc = SelfCorrectingAgent(agent, corrector)

    result = sc.run_with_log("What is 2+2?")
    assert "attempts" in result
    assert "final_answer" in result
    assert len(result["attempts"]) == 1
    assert result["attempts"][0]["passed"] is True


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
