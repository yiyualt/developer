LCEL Philosophy
================

Before LCEL, building a chain was imperative — you knew the class names,
constructor parameters, and wiring. With LCEL, you just write the data
flow: ``prompt | llm | parser``.

The ``|`` operator
------------------

The pipe (``|``) is borrowed from Unix. In Unix, ``grep | sort | head``
pipes text through programs. In LCEL, ``prompt | llm | parser`` pipes
data through components.

.. code-block:: python

   # Before LCEL: imperative
   chain = LLMChain(
       prompt=PromptTemplate("Tell me about {topic}"),
       llm=OpenAI(),
       output_parser=JsonOutputParser(),
   )
   result = chain.run(topic="Python")

   # After LCEL: declarative
   chain = PromptTemplate("Tell me about {topic}") | OpenAI() | JsonOutputParser()
   result = chain.invoke({"topic": "Python"})

The Runnable interface
-----------------------

LCEL works because every component implements the same interface:

.. code-block:: text

   Runnable.invoke(input) -> output

   PromptTemplate.invoke(vars: dict)     -> str
   LLM.invoke(prompt: str)             -> str
   OutputParser.invoke(text: str)      -> Any

When you write ``prompt | llm``, the ``|`` operator returns a
``RunnableSequence``. When ``invoke()`` is called, data flows
left to right — each component's output becomes the next's input.

Why Runnable matters
--------------------

Runnable is the foundation for everything that came after in
LangChain's evolution:

- ``invoke`` — synchronous execution
- ``ainvoke`` — async execution (future)
- ``stream`` — streaming output (future)
- ``batch`` — batch execution (future)
- ``bind`` — parameter binding (future)

A single interface, many execution modes. LCEL is not just
syntactic sugar — it's the architectural foundation.
