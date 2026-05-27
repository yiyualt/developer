Agent Design
============

SequentialChain chains LLM calls in a fixed order. But real reasoning
often requires *dynamic* decision-making: the LLM must choose what to
do next based on what it observes. This is the ReAct (Reasoning +
Acting) paradigm introduced by Yao et al. (2022).

The ReAct loop
---------------

In each iteration, the Agent follows this pattern:

.. code-block:: text

   Thought: I need to calculate 2+3 to answer this question.
   Action: calculator[2+3]
   Observation: 5

   Thought: I now know the answer.
   Final Answer: 5

The loop continues until the LLM produces a **Final Answer** or
``max_iterations`` is reached.

.. code-block:: text

   ┌─────────────┐
   │  Question   │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │   Thought   │────▶│   Action    │────▶│ Observation │
   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
          │                    │                     │
          │                    │                     │
          ▼                    ▼                     ▼
   Final Answer?          Tool execution        Append to
   (yes → done)           (invoke Tool)         scratchpad
          │                                         │
          │  no                                      │
          └─────────────────────────────────────────┘
                        repeat loop

Tool interface
--------------

Every Tool exposes three attributes:

- ``name``: identifier used in Action parsing (e.g. "calculator")
- ``description``: short text explaining what the tool does, included
  in the ReAct prompt so the LLM knows when to use it
- ``run(input: str) -> str``: executes the tool and returns a result

The Agent builds the ReAct prompt with tool names and descriptions,
allowing the LLM to choose the right tool based on the question.

Output parsing
--------------

AgentOutputParser extracts structured data from each LLM response:

- ``Thought: ... Action: tool[input]`` → **AgentAction** (call a tool)
- ``Thought: ... Final Answer: ...`` → **AgentFinish** (terminate)
- No markers found → **AgentFallback** (treat as a Thought, continue)

On malformed output, the parser falls back gracefully rather than
crashing, so the Agent can keep reasoning.

Max iterations
---------------

The loop has a hard limit (default 5). If the LLM never produces a
Final Answer within the limit, the Agent returns the most recent
Thought as the answer. This prevents infinite loops from LLMs that
get stuck in repetitive reasoning.