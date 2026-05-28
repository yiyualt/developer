Streaming Philosophy
====================

Why streaming?
--------------

LLM calls take seconds — sometimes 10+ seconds for a complex prompt.
In that time the user stares at a blank screen, wondering if anything
is happening. Streaming solves this by yielding tokens as they arrive,
creating a "the model is thinking" experience that mirrors how humans
read and write.

The key insight: **streaming is a UX dimension, not a throughput dimension**.
A streaming response takes the same wall-clock time as a blocking one.
The benefit is perceived responsiveness, not faster execution.

run() vs stream()
-----------------

LangChain provides two parallel interfaces for LLM interaction:

- ``run()`` — blocking, returns the full response as a string.
  Used by programmatic callers that need the complete result before
  proceeding (e.g. SequentialChain, Agent _run_loop).

- ``stream()`` — non-blocking, yields tokens one at a time via a
  generator. Used by human-facing interfaces (CLI, notebook, web UI)
  where real-time display matters.

These are *parallel* interfaces, not replacements. ``run()`` remains
the primary API for chain composition; ``stream()`` is the display
layer. A chain that calls ``run()`` internally can still expose
``stream()`` at the top level.

Token-level vs step-level streaming
------------------------------------

Different components stream at different granularities:

- **LLMChain.stream()** — token-level. Each yielded item is a single
  token string. Useful for real-time text display.

- **Agent.stream()** — step-level. Each yielded item is a dict with
  ``type`` (thought/action/observation/final_answer) and ``content``.
  This is coarser because Agent reasoning is inherently multi-step:
  each step depends on the previous observation, so we can't stream
  the "next thought" until the current tool finishes.

The pattern: stream at whatever granularity the component naturally
produces. Don't force token-level streaming on a step-level process.

on_llm_new_token and the callback ecosystem
-------------------------------------------

Streaming adds ``on_llm_new_token`` to the CallbackHandler interface.
This is a *high-frequency* hook — it fires once per token, which can
be 50-200 times per response. This makes it fundamentally different
from the other hooks (which fire once per execution step).

The StdOutCallbackHandler implements ``on_llm_new_token`` by printing
each token with ``flush=True``, enabling real-time terminal display.
Custom handlers should be cautious: logging every token to a file or
database creates I/O overhead that can slow down the stream.

Design constraint: we did NOT add ``on_agent_step`` or similar hooks
for Agent streaming. The existing ``on_agent_action`` and
``on_agent_finish`` hooks already cover Agent execution steps.
Streaming just yields those steps as a generator — no new hooks needed.

DashScope streaming gotcha
--------------------------

DashScope (and some other OpenAI-compatible providers) send a final
chunk with an empty ``choices`` list after the streaming response
completes. This causes ``chunk.choices[0]`` to raise IndexError if
not guarded. The fix:

.. code-block:: python

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.content is not None:
            yield delta.content

This is a provider-specific behavior, not an OpenAI API spec issue.
Any LLM subclass implementing ``_stream`` must handle edge cases in
the streaming response format.