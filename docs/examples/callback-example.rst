Callback Example
================

This example demonstrates how to observe execution using
``StdOutCallbackHandler`` — the built-in handler that prints
events to your terminal.

StdOutCallbackHandler with LLMChain
------------------------------------

.. code-block:: python

   from langchain import (
       PromptTemplate, OpenAI, LLMChain, StdOutCallbackHandler,
   )

   prompt = PromptTemplate(
       input_variables=["question"],
       template="Answer this question concisely: {question}",
   )

   handler = StdOutCallbackHandler()
   chain = LLMChain(prompt=prompt, llm=OpenAI(), callbacks=[handler])

   print(chain.run(question="What is Python?"))

   # stdout output:
   # [LLMChain] Start: {'question': 'What is Python?'}
   # [LLM] Start: Answer this question concisely: What is Python?
   # [LLM] End: Python is a programming language
   # [LLMChain] End: Python is a programming language
   # Python is a programming language

StdOutCallbackHandler with Agent
---------------------------------

.. code-block:: python

   from langchain import (
       Agent, OpenAI, CalculatorTool, StdOutCallbackHandler,
   )

   handler = StdOutCallbackHandler()
   agent = Agent(
       llm=OpenAI(),
       tools=[CalculatorTool()],
       callbacks=[handler],
   )

   print(agent.run(question="What is 2 + 3?"))

   # stdout output:
   # [Agent] Action: calculator[2+3]
   # [Tool] Start: calculator(2+3)
   # [Tool] End: 5
   # [Agent] Finish: 5
   # 5

Custom CallbackHandler
----------------------

Create your own handler by subclassing ``CallbackHandler``:

.. code-block:: python

   from langchain import CallbackHandler

   class LoggingHandler(CallbackHandler):
       def on_chain_start(self, **kwargs):
           print(f"Chain started with: {kwargs.get('inputs')}")

       def on_llm_end(self, **kwargs):
           print(f"LLM responded: {kwargs.get('response')}")

       def on_error(self, **kwargs):
           print(f"Error occurred: {kwargs.get('error')}")

   handler = LoggingHandler()
   chain = LLMChain(prompt=prompt, llm=OpenAI(), callbacks=[handler])