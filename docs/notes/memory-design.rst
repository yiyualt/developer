Memory Design
=============

LLMChain and Agent are stateless — every ``run()`` starts from
scratch. But real applications need conversation history: the user
asks a follow-up question, and the LLM should remember what was
said before.

Memory solves this by automatically saving and loading conversation
history across ``run()`` calls.

The Memory interface
---------------------

Every Memory implementation exposes three methods:

- ``save_context(inputs, outputs)``: store one round (Human input +
  AI output)
- ``load_context() -> str``: return formatted history ready to
  prepend to a prompt
- ``clear()``: reset stored history

The history format is alternating ``Human: ...`` and ``AI: ...``
lines, which LLMs naturally understand as a conversation log.

Buffer vs Window vs Summary
----------------------------

Three implementations cover different tradeoffs:

.. code-block:: text

   BufferMemory         WindowMemory             SummaryMemory
   ────────────────     ──────────────────       ──────────────────
   Stores ALL history   Stores ALL, returns       Compresses old
                        last K rounds             rounds into summary
   Returns everything   Returns last K            Returns summary +
                        rounds                    recent rounds
   Prompt grows         Prompt bounded            Prompt bounded
   indefinitely         (discards old info)       (preserves key facts)
   No LLM calls         No LLM calls              LLM call per
                        needed                    compression

   Use Buffer when:     Use Window when:         Use Summary when:
   - Short chats        - Only recent context     - Long conversations
   - Full context       matters                   - Key facts must survive
     needed              - Can afford to lose      - Prompt budget is tight
                          older details

   SummaryMemory needs an LLM instance — the compression quality
   depends on the LLM's ability to preserve key information.
   Each compression adds an extra LLM call, so it's best used
   when conversations are genuinely long.

Integration with Agent
----------------------

Agent also accepts a ``memory`` parameter. The loaded history is
prepended to the ReAct scratchpad, giving the LLM context from
prior conversations.

After the loop finishes, the full reasoning process is saved to
memory — not just the Final Answer. This includes all Thoughts,
Actions, Observations, and the Final Answer, giving future
conversations visibility into the Agent's reasoning:

.. code-block:: text

   Memory saves:
   Human: What is Paris's population?
   AI: Thought: I should search for this
       Action: search[Paris population]
       Observation: 2.2 million
       Final Answer: Paris has about 2.2 million people

   Next conversation can see what the Agent searched for
   and what it learned — avoiding redundant tool calls.

Memory is distinct from the Agent's ReAct scratchpad: the
scratchpad is a single-loop temporary log, while Memory persists
across multiple ``run()`` calls.