Plan-and-Execute Philosophy
============================

Every Agent so far answers a question. ``run(question="What is 2+3?")``
returns ``"5"``. But real tasks aren't single questions — they're goals
that require multiple steps, each building on the last.

Plan-and-Execute is the leap from "answer a question" to "achieve a goal".

Why not just use ReAct?
-----------------------

ReAct is great for iterative reasoning — when you don't know how many
steps you need and each step's observation informs the next. But for goals
with a known structure, ReAct is wasteful: it re-reasons about "what
should I do next" when the structure was already clear from the start.

.. code-block:: text

   ReAct Agent:                    PlanAndExecute Agent:
   ──────────────                  ──────────────────────────
   Q: "Write a report on EVs"      Goal: "Write a report on EVs"

   Thought: I should research.     Plan:
   Action: search[EV market]        1. Research EV market data
   Observation: [data]               2. Research EV brands
   Thought: I should research more.  3. Analyze findings
   Action: search[EV brands]         4. Write report
   Observation: [data]
   Thought: I have enough.         Execute:
   Final Answer: [report]            Step 1 → [market data]
                                     Step 2 → [brands data]
   ─ 浪费：每步都在推理"下一步         Step 3 → [analysis]
   做什么"，但结构是预知的             Step 4 → [report]

Plan-and-Execute separates **what to do** (planning) from **doing it**
(execution). This separation makes the process transparent and the
intermediate results inspectable.

The two-phase design
--------------------

.. code-block:: text

   ┌──────────────┐     ┌─────────────────────────────────┐
   │ Phase 1:     │     │ Phase 2: Execute                │
   │ Plan         │     │                                 │
   │              │     │ For each step:                   │
   │ LLM generates│     │   build_prompt(                  │
   │ a numbered   │     │     goal, plan,                  │
   │ list of      │────▶│     previous results,            │
   │ steps        │     │     current step                 │
   │              │     │   )                              │
   │ "1. Research │     │   → LLM or AgentTool executes    │
   │  2. Analyze  │     │   → collect result               │
   │  3. Write"   │     │                                 │
   └──────────────┘     └─────────────────────────────────┘
                                │
                                ▼
                        final_answer: string
                        full log: plan + each step result

Phase 1 deliberately produces a **complete, visible plan**. This is not
an internal detail — it's a product. Users can inspect the plan, modify
it, or save it for documentation.

Phase 2 executes each step with **full context**: the original goal,
the complete plan, all previous step results, and the current step.
This means step 3 knows what step 1 discovered, even if they handle
different aspects of the task.

Why static plans (for now)?
----------------------------

The v1 plan is static — once generated, it doesn't change. This is
deliberately simpler than dynamic replanning. A static plan:

- Is predictable (you know what will happen)
- Is debuggable (you can see where it went wrong)
- Has a clear scope (no infinite replanning loops)

Dynamic replanning — adjusting the plan based on intermediate results —
is a natural v2 evolution. The open question: should replanning happen
after each step, or only when a step fails?

Context accumulation vs summarization
--------------------------------------

Each step sees ALL previous results. For short plans (3-7 steps), this
is manageable. For longer plans, the prompt grows linearly.

Two strategies for future versions:

1. **Summarization**: After each step, summarize the result into one
   sentence. Only the summaries are passed forward, not full results.
2. **Sliding window**: Only the last N step results are shown in full;
   earlier results are summarized.

Neither is implemented in v1. The motivation is to keep the context
rich and complete until the need for compression is demonstrated.

The AgentTool connection
-------------------------

PlanAndExecuteAgent integrates naturally with AgentTool (added in the
previous version):

.. code-block:: python

   agent = PlanAndExecuteAgent(
       llm=llm,
       tools=[
           SearchTool(),
           AgentTool(name="analyst", agent=analysis_agent),
           AgentTool(name="writer", agent=writing_agent),
       ],
   )
   agent.run(goal="Research and write a report on Python's popularity")

Each step can be executed by a specialist Agent, wrapped as a Tool.
The PlanAndExecuteAgent becomes an orchestrator that decomposes
goals and delegates to specialists — combining the two most recent
additions to LangChain.

From question to goal
---------------------

This is the conceptual heart of Plan-and-Execute:

.. code-block:: text

   Before:  Agent.run(question="What is...")
            → one question, one answer

   After:   PlanAndExecuteAgent.run(goal="Create a...")
            → one goal, many steps, synthesized result

The Agent solves problems. The PlanAndExecuteAgent achieves goals.
