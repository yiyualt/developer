Simple Q&A Example
===================

A minimal, runnable example of a LangChain question-answering chain
using a real LLM via DashScope.

.. code-block:: python

   from langchain.prompts import PromptTemplate
   from langchain.llms import OpenAI
   from langchain.chains import LLMChain

   # Define a prompt template
   prompt = PromptTemplate(
       "Answer this question concisely: {question}"
   )

   # Set up LLM (reads from .env)
   llm = OpenAI()

   # Compose the chain
   chain = LLMChain(prompt=prompt, llm=llm)

   # Run single queries
   print(chain.run(question="What is Python?"))

   # Run batch queries
   results = chain.apply([
       {"question": "What is Python?"},
       {"question": "What is LangChain?"},
   ])
   print(results)

Key Points
----------

- ``PromptTemplate`` handles input formatting — the chain never sees raw inputs
- ``OpenAI`` reads configuration from ``.env`` (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL)
- ``LLMChain.run()`` for single queries, ``LLMChain.apply()`` for batch
- Swap the ``.env`` config to use a different provider without changing any code