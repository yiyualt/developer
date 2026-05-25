Sequential Chain Design
=======================

Multi-step reasoning requires chaining multiple LLM calls together:
step 1's output becomes step 2's input, and so on. SequentialChain
implements this pattern with a key-based data flow mechanism.

Key-based data flow
-------------------

Each LLMChain declares ``output_keys`` — the variable names it
produces. When a chain runs inside a SequentialChain, its output
is always a dict keyed by ``output_keys``. SequentialChain merges
each step's output dict into the accumulated input pool, so
subsequent chains can reference prior outputs by key name.

.. code-block:: text

   Input: {"subject": "Python"}
        │
        ▼
   Step 1: LLMChain → {"topic": "Python"}
        │          accumulated: {"subject": "Python", "topic": "Python"}
        ▼
   Step 2: LLMChain(prompt needs {topic}) → {"summary": "..."}
        │          accumulated: {"subject": "Python", "topic": "Python", "summary": "..."}
        ▼
   Output: {"subject": "Python", "topic": "Python", "summary": "..."}

The key names in each step's output must match the variable names
in the next step's PromptTemplate for automatic data flow. If keys
don't match, you need to redesign your prompt templates or add
explicit mapping (future feature).

output_keys behavior
--------------------

LLMChain's ``output_keys`` property determines what a chain declares
as its output variables:

- **No parser**: ``output_keys`` defaults to ``["text"]``, and the
  raw LLM response is wrapped as ``{"text": result}```.
- **JsonOutputParser**: ``output_keys`` reflects the expected JSON
  dict keys, and the parsed dict is returned directly.
- **Other parsers**: ``output_keys`` falls back to ``["text"]`` and
  the parsed value is wrapped under that key.

This distinction matters because ``run()`` returns a bare value for
single-step convenience, while ``_call_internal()`` returns a dict
for composition within SequentialChain.

Accumulated output
------------------

SequentialChain's ``run()`` returns a dict containing *all* output
keys from *every* step, not just the final step. This preserves
intermediate results that the user may need later.

If only the final step's output is desired, the user can extract
the relevant keys from the returned dict.

Input validation
----------------

SequentialChain validates inputs at two levels:

1. **Initial inputs**: all ``input_variables`` declared on the
   SequentialChain must be provided in the ``run()`` call.
2. **Per-chain requirements**: each chain's PromptTemplate
   ``input_variables`` must be satisfied by the initial inputs
   combined with prior step outputs.

Missing variables raise a ``KeyError`` with a descriptive message
indicating which variables are unsatisfied and what keys are
available.