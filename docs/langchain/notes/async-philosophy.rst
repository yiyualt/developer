Async Philosophy
================

Why minimal async?
------------------

Async is a powerful abstraction — but in LangChain, we deliberately
scoped it to the *minimum useful surface*:

- ``LLM.agenerate(prompts)`` — async concurrent LLM calls
- ``LLMChain.apply_async(input_list)`` — async concurrent chain calls

That's it. No async ``run()``, no async ``Agent``, no async Memory.
Why?

**The cost of full-system async.** Making every method async adds
complexity everywhere: async constructors, async I/O, async
context managers. It forces callers into ``asyncio`` even for
single-shot use cases. And it creates a bifurcated API surface —
every method has a sync and async twin, doubling the maintenance
burden without doubling the value.

The real win from async is **concurrency** — running multiple LLM
calls in parallel. ``agenerate()`` and ``apply_async()`` deliver
that win with minimal API surface. Everything else can stay sync.

asyncio.gather vs ThreadPoolExecutor
-------------------------------------

Python has two concurrency mechanisms: ``asyncio`` (cooperative
I/O multiplexing) and ``ThreadPoolExecutor`` (OS threads). We chose
``asyncio.gather`` for ``_agenerate()`` because:

1. **OpenAI's Python SDK already provides AsyncOpenAI.** The
   async client exists; using it is the natural choice.
2. **LLM calls are I/O-bound.** The runtime is dominated by
   waiting for the API response, not CPU work. Async I/O
   multiplexing is the right model for this.
3. **No thread-safety concerns.** AsyncOpenAI's ``await`` points
   are safe; no shared state, no locks, no race conditions.

ThreadPoolExecutor would work too, but it adds thread management
complexity and doesn't leverage the existing AsyncOpenAI client.
``asyncio.gather`` is the simpler path.

Fallback strategy
-----------------

Not every LLM subclass will implement ``_agenerate()``. The base
class provides a default fallback:

.. code-block:: python

    async def _agenerate(self, prompts):
        return self._generate(prompts)  # fall back to sync

This means calling ``agenerate()`` on a subclass that hasn't
implemented async still works — it just runs synchronously. No
crashes, no ``NotImplementedError``, just no concurrency benefit.

This is different from ``_stream()`` which raises
``NotImplementedError`` when not implemented. The reasoning:
streaming is a *display* feature — if you call ``stream()`` on a
model that can't stream, you want an explicit error. Async is a
*performance* feature — if you call ``agenerate()`` on a model
that can't go async, you still get correct results, just slower.

Order preservation
------------------

``asyncio.gather`` returns results in the same order as input
prompts, even though they execute concurrently. This is critical
for ``apply_async()`` — the caller expects ``output[i]`` to
correspond to ``input_list[i]``. ``asyncio.gather`` guarantees
this without requiring manual index tracking.