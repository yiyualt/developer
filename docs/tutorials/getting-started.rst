Getting Started
===============

This tutorial walks you through building and running your first LangChain
chain—from configuration to execution in under 5 minutes.

What You'll Build
-----------------

A simple question-answering chain that takes a topic, formats a prompt,
and returns an LLM response.

.. code-block:: python

   >>> from langchain.prompts import PromptTemplate
   >>> from langchain.llms import OpenAI
   >>> from langchain.chains import LLMChain

   >>> prompt = PromptTemplate("Tell me about {topic}")
   >>> llm = OpenAI()  # reads from .env
   >>> chain = LLMChain(prompt=prompt, llm=llm)

   >>> chain.run(topic="Python")

Step 1: Create a PromptTemplate
--------------------------------

A ``PromptTemplate`` turns a template string with ``{variable}`` placeholders
into a complete prompt:

.. code-block:: python

   >>> from langchain.prompts import PromptTemplate

   >>> prompt = PromptTemplate("What is {topic}?")
   >>> prompt.input_variables
   ['topic']

   >>> prompt.format(topic="Python")
   'What is Python?'

Step 2: Set Up an LLM
----------------------

``OpenAI`` is the LLM implementation that calls OpenAI-compatible APIs.
It reads configuration from a ``.env`` file in the project root.

Create a ``.env`` file::

   LLM_API_KEY=sk-xxx
   LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   LLM_MODEL=glm-5.1

Then use the LLM::

   >>> from langchain.llms import OpenAI

   >>> llm = OpenAI()  # reads from .env
   >>> llm.generate(["What is Python?"])
   ['Python is a high-level, general-purpose programming language...']

Or configure explicitly::

   >>> llm = OpenAI(
   ...     model_name="glm-5.1",
   ...     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
   ...     openai_api_key="sk-xxx",
   ... )

Step 3: Compose a Chain
-----------------------

``LLMChain`` wires a PromptTemplate and an LLM together:

.. code-block:: python

   >>> from langchain.chains import LLMChain

   >>> chain = LLMChain(prompt=prompt, llm=llm)
   >>> chain.run(topic="Python")
   'A programming language'

That's it — **prompt + llm = chain**. This is the fundamental primitive
that everything in LangChain builds upon.

What's Next?
-------------

- Read :doc:`/notes/chain-design-philosophy` to understand *why* this design
- See :doc:`/examples/simple-qa` for a complete runnable example