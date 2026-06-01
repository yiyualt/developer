Chat Model Philosophy
=====================

From the beginning, LangChain treated prompts as strings. ``PromptTemplate``
produces a string. ``LLM.generate()`` receives a list of strings. Memory
appends a string. Everything is a string.

But the underlying API — OpenAI's Chat Completions — has always supported
*roles*: ``system``, ``user``, ``assistant``. We just flattened them into
strings. Chat Model makes the roles explicit.

Why roles matter
----------------

A string doesn't know who said it:

.. code-block:: python

   # Before: roles are lost
   prompt = "You are a math tutor.\n\nWhat is 2+2?"
   llm.generate([prompt])
   # → OpenAI wraps everything as {"role": "user"}

With message types, the LLM sees the correct structure:

.. code-block:: python

   # After: roles are explicit
   openai.generate_messages([[
       SystemMessage("You are a math tutor."),
       HumanMessage("What is 2+2?"),
   ]])
   # → API receives [{"role": "system", ...}, {"role": "user", ...}]

This matters because models are trained to respond differently to
different roles. A ``system`` message sets the assistant's behavior.
A ``user`` message is a question. An ``assistant`` message is history.

Two worlds coexist
------------------

.. code-block:: text

   String world (existing)          Message world (new)
   ───────────────────────          ─────────────────────
   PromptTemplate                   ChatPromptTemplate
   LLM.generate(prompts: list[str]) OpenAI.generate_messages(messages)
   "Hello {name}"                   [SystemMessage("You are {role}"),
                                      HumanMessage("Hello {name}")]

Both work side by side. Nothing breaks. ``LLMChain`` still uses strings.
New code can opt into messages where roles add value.

ChatPromptTemplate vs PromptTemplate
-------------------------------------

``PromptTemplate`` operates on one string:

.. code-block:: python

   template = PromptTemplate("Tell me about {topic}")
   result = template.format(topic="Python")
   # → "Tell me about Python"  (one string)

``ChatPromptTemplate`` operates on a list of messages:

.. code-block:: python

   template = ChatPromptTemplate([
       SystemMessage("You are a {role}."),
       HumanMessage("Tell me about {topic}."),
   ])
   result = template.format(role="historian", topic="Python")
   # → [SystemMessage("You are a historian."),
   #    HumanMessage("Tell me about Python.")]

The key difference: ``ChatPromptTemplate`` preserves the message types
through formatting. Each message's content is a template, but the role
is fixed.

What's not here yet
-------------------

- Message-aware Memory (storing conversation as messages instead of strings)
- ``generate_messages`` on the LLM ABC (currently only on OpenAI)
- ``ChatLLMChain`` (a chain that works with messages natively)
- Function / Tool messages

These are all later evolutions. The current version introduces the
fundamental data types and the simplest template — just enough to
make roles explicit.
