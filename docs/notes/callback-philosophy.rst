Callback Design Philosophy
==========================

LangChain's execution flows are complex — chains call LLMs, agents
loop through thoughts and actions, tools produce observations. But
all of this happens invisibly. The developer calls ``chain.run()``
and gets a string back, with no way to see what happened inside.

Callback solves this by opening a window into execution. Components
invoke lifecycle hooks at key points, and handlers receive those
events for logging, debugging, or tracing.

Why Handler, Not EventStream
-----------------------------

Two common patterns for execution observation:

.. code-block:: text

   Handler pattern            EventStream pattern
   ─────────────             ────────────────────
   Component calls           Component emits
   handler.on_llm_start()    event("llm_start")

   Handler is a method       Event is a data object
   on a concrete class       consumed by subscribers

   Simple, direct            Flexible, decoupled

We chose the **Handler pattern** for the same reason real LangChain
did: it's the simplest thing that works. Each component keeps a
``callbacks`` list and calls hook methods in order. No event queue,
no subscriber registry, no async — just method calls.

The EventStream pattern is more flexible (multiple consumers,
filtering, replay) but adds complexity that isn't needed yet. As
LangChain grows, it may evolve toward event streams, but the
Handler pattern is the right starting point — it matches the
project's philosophy of "build the simplest version first."

Event Granularity
-----------------

The first version defines 9 hooks covering the main execution paths:

.. code-block:: text

   LLMChain execution:
     on_chain_start → on_llm_start → on_llm_end → on_chain_end

   Agent ReAct loop:
     on_agent_action → on_tool_start → on_tool_end → on_agent_finish

   Error path:
     on_error (from any component)

Memory and prompt formatting are internal steps — they don't have
hooks yet. This is intentional: start with the most valuable
events (LLM calls, chain boundaries, agent reasoning), add more
granularity when real use cases demand it.

Hooks use ``**kwargs`` so future extensions (token counts, timing,
model metadata) can be added without breaking existing handlers.

Callback Propagation
--------------------

This version does **not** propagate callbacks through nested chains.
When SequentialChain calls a sub-chain, the sub-chain's callbacks
are only the ones it was given at construction — not the parent's.

Real LangChain later added callback propagation (parent passes
callbacks to children), which is the natural evolution. But for
this version, keeping propagation out simplifies the implementation
and makes the boundary clear: each component owns its own callbacks.

The ``_fire()`` helper
----------------------

Every component with callbacks has a ``_fire(event, **kwargs)`` method
that iterates over ``self.callbacks`` and calls the matching hook.
This is a small convenience that avoids repeating the loop everywhere.

.. code-block:: python

   def _fire(self, event: str, **kwargs) -> None:
       for handler in self.callbacks:
           getattr(handler, event)(**kwargs)

Why not a CallbackManager? Because a manager adds indirection
(handler registration, priority ordering, filtering) that isn't
needed with 1-2 handlers. If callback management becomes complex,
the manager pattern is the natural next step.

Tool's run() vs _run()
----------------------

To add callbacks to Tool without changing existing subclasses,
``run()`` became the public entry point that fires hooks and calls
``_run()`` — the abstract method subclasses implement. This is a
minor API change: existing Tool subclasses rename ``run`` to
``_run`` and everything works.

This pattern (public method with hooks, internal method with logic)
is the same one real LangChain used for many components.

Relation to Real LangChain
--------------------------

Real LangChain's callback system evolved through several stages:

1. **v0.0.1**: Simple ``CallbackManager`` with ``on_llm_start/end``
2. **v0.0.2**: Added chain and tool hooks
3. **v0.0.3**: Callback propagation through nested chains
4. **v0.1.0**: Async callbacks, streaming, ``BaseCallbackManager``
5. **v0.2.0**: LangSmith tracing integration

Our version sits at stage 2 — enough hooks to observe the main
paths, no propagation or async. The next natural evolution would
be propagation (stage 3), then async and streaming (stage 4).