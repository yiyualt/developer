Self-Correction Philosophy
=========================

Agent produces an answer. But is it a *good* answer? Self-Correction
adds a validation step after the Agent: check the output, and if
something's wrong, tell the Agent what to fix and ask it to try again.

This is the first step from "produce answers" to "produce reliable
answers."

The core loop
-------------

.. code-block:: text

   question ──▶ Agent.run() ──▶ answer
                                      │
                                      ▼
                               ┌─────────────┐
                               │ LLMCorrector │ "Does this look right?"
                               │ .check()     │
                               └──────┬──────┘
                                      │
                            ┌─────────┴─────────┐
                            │                   │
                            ▼                   ▼
                          PASS                FAIL
                       return answer    ┌──────────────┐
                                        │ Append feedback│
                                        │ to question    │
                                        │ Retry Agent    │
                                        └──────┬─────────┘
                                               │
                                               ▼
                                          Agent.run(question + feedback)
                                          (loop continues, max max_retries)

Why a separate Corrector?
--------------------------

The Corrector is independent from the Agent. This means:

- Any Agent can be corrected (ReAct, PlanAndExecute, etc.)
- The Corrector can be swapped (LLM-based, rule-based, etc.) without
  changing the Agent
- The quality standard is configurable ("be stricter" vs "be lenient")

The current v1 LLMCorrector is simple: ask an LLM "is this right?"
A "PASS" response means the answer is accepted. Anything else is
treated as feedback for the retry.

Why wrapping, not inheritance?
-------------------------------

SelfCorrectingAgent wraps an Agent rather than extending it:

.. code-block:: python

   # Any Agent can be corrected
   sc = SelfCorrectingAgent(
       agent=Agent(llm=llm, tools=[...]),
       corrector=LLMCorrector(llm=llm),
   )
   sc.run("What is 2+2?")  # ← automatic validation + retry

This is the same composition pattern as AgentTool: wrap something
to add a capability without changing the wrapped object.

Limitations of v1
-----------------

- Corrector is always LLM-based — no rule-based JSON schema checking yet
- Feedback is appended to the question string — not structured
- No partial correction ("keep the good parts, fix only the bad ones")
- LLM corrector can hallucinate false positives/negatives
