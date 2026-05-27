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

Buffer vs Window
-----------------

Two implementations cover the core tradeoff: completeness vs length.

.. code-block:: text

   ConversationBufferMemory          ConversationBufferWindowMemory
   ──────────────────────────────    ──────────────────────────────────
   Stores ALL history                 Stores ALL, returns last K rounds
   load_context() → everything        load_context() → last K rounds
   Prompt grows indefinitely          Prompt stays bounded

   Use Buffer when:                   Use Window when:
   - Short conversations              - Long or repeated conversations
   - Full context needed              - Only recent context matters

Integration with LLMChain
--------------------------

When ``LLMChain`` is created with a ``memory`` parameter, ``run()``
automatically:

1. Loads conversation history via ``memory.load_context()``
2. Prepends it to the formatted prompt
3. After execution, saves the input/output via ``memory.save_context()``

Without memory, ``run()`` behaves exactly as before — fully
stateless. This is backward-compatible.

Integration with Agent
----------------------

Agent also accepts a ``memory`` parameter. The loaded history is
prepended to the ReAct scratchpad, giving the LLM context from
prior conversations. After the loop finishes, the question and
final answer are saved to memory.

Memory is distinct from the Agent's ReAct scratchpad: the
scratchpad is a single-loop temporary log, while Memory persists
across multiple ``run()`` calls.