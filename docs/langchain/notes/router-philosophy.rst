Router Philosophy
=================

All chains so far follow fixed execution paths: SequentialChain
runs A→B→C, RetrievalChain runs embed→search→generate. No
branching, no choice — the pipeline is predetermined.

Router Chain breaks this pattern. It examines the user's question
and *chooses* which Chain to execute. This is LangChain's first
step from "linear pipeline" to "dynamic orchestration".

The Dynamic Option Injection pattern
--------------------------------------

Router and Agent share the same fundamental design pattern:

.. code-block:: text

   ┌─────────────────────────────────────────────┐
   │  "Dynamic Option Injection"                 │
   ├─────────────────────────────────────────────┤
   │                                             │
   │  1. Define available options                │
   │     Agent:  Tool.name + Tool.description    │
   │     Router: Destination.name + Destination  │
   │              .description                    │
   │                                             │
   │  2. Auto-format options into the prompt     │
   │     Agent:  "You have access to: calc, ..." │
   │     Router: "Available chains: retrieval,.."│
   │                                             │
   │  3. LLM selects one option                  │
   │     Agent:  "Action: calculator[2+3]"       │
   │     Router: '{"chain": "retrieval"}'        │
   │                                             │
   │  4. Execute the selected option              │
   │     Agent:  Tool.run(input)                 │
   │     Router: Chain.run(question)              │
   └─────────────────────────────────────────────┘

   Agent selects at micro-level (which tool to call)
   Router selects at macro-level (which chain to run)

   This pattern appears again and again in LangChain's evolution.
   Understanding it unlocks the design philosophy behind both
   Agent and Router — they're not separate inventions, they're
   the same idea applied at different scales.

Router vs Agent — when to use which?
--------------------------------------

.. code-block:: text

   Router (one decision, then delegate)           Agent (many decisions in a loop)
   ──────────────────────────────────            ───────────────────────────────────
   Select a chain, execute it fully               Select a tool, observe, repeat
   One routing step                               Multiple reasoning steps
   "Which pipeline should handle this?"           "What tool should I call next?"

   Use Router when:                               Use Agent when:
   - You have distinct processing pipelines       - The task needs iterative reasoning
   - Each pipeline handles a different domain     - The answer requires tool chaining
   - One routing decision is enough               - Observations feed into next step

   They can be combined: Router selects a pipeline,
   and that pipeline might contain an Agent.

Why JSON output for routing?
-----------------------------

The Router asks the LLM to output ``{"chain": "name"}`` and
parses it with JsonOutputParser. Why not just ask the LLM to
output the chain name directly?

Because LLMs are unreliable with free-form output. They often
add explanatory text ("I think the best chain is retrieval")
or produce unexpected formats. JSON constrains the output
structure, making parsing more reliable.

We reuse the existing JsonOutputParser — no new parsing
component needed. This is a principle: before inventing a
new mechanism, check if an existing one does the job.

Fallback — when the router gets confused
-----------------------------------------

LLMs can fail to produce valid JSON or select a non-existent
chain name. Rather than throwing an exception, LLMRouterChain
falls back to a default destination.

The default chain should be the safest, most general option —
typically a plain LLMChain that can handle any question
without specialized tools or document access.

What we don't have yet
-----------------------

- EmbeddingRouterChain (use similarity instead of LLM call — faster)
- MultiRoute (route to multiple chains in parallel)
- Routing to SequentialChain (needs input mapping across steps)

These are all later evolutions. The current version is the
earliest, simplest form of routing — one LLM call, one choice,
one execution.