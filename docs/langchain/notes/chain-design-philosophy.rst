Chain Design Philosophy
========================

Why "Chain"?
------------

LangChain's name comes from its simplest primitive: **prompt + llm = chain**.

A chain is a composable unit that takes input, processes it through a
sequence of steps, and produces output. In v0.0.1, that sequence has
exactly two steps:

1. **Format**: PromptTemplate substitutes variables into a template string
2. **Generate**: LLM produces a response from the formatted prompt

.. code-block:: text

   # The chain's execution path:
   inputs -> PromptTemplate.format() -> formatted_prompt -> LLM.generate() -> response

Why This Matters
-----------------

This two-step composition is deliberately minimal. It solves exactly one
problem: *"how do I reliably turn a question into an answer using an LLM?"*

Every subsequent feature in LangChain—Agents, Memory, Retrieval, LCEL—
extends this pattern. The chain is the **genetic code** of the framework.

Composability Over Features
----------------------------

The design prioritizes composability over feature richness. A chain with
only two steps is trivially understandable, trivially testable, and
trivially extensible. You don't need to understand the whole framework
to use a chain — you just need to understand two things:

- What goes in (input variables)
- What comes out (a string)

This is the same philosophy as Unix pipes: each program does one thing
well, and programs compose through a standard interface (text streams).
In LangChain, the standard interface is **string → string**.

The LLM Interface
------------------

The ``LLM`` abstract base class defines a single contract:
``generate(list[str]) -> list[str]``. Any provider—OpenAI, DashScope,
or a future local model—implements this same interface.

This means chain logic is completely independent of which model you use.
The ``OpenAI`` class works with any OpenAI-compatible endpoint, configured
via ``.env`` or constructor parameters. Swap the model, keep the chain.

Configuration via ``.env``
---------------------------

The ``OpenAI`` class reads from a ``.env`` file in the project root::

   LLM_API_KEY=sk-xxx
   LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   LLM_MODEL=glm-5.1

This makes it easy to switch providers without changing code—just update
the ``.env`` file. Constructor parameters take precedence if you need
to override for a specific call.