Memory Example
==============

This example demonstrates conversation memory — automatically
saving and loading history across multiple ``run()`` calls.

ConversationBufferMemory with LLMChain
----------------------------------------

.. code-block:: python

   from langchain import PromptTemplate, OpenAI, LLMChain, ConversationBufferMemory

   prompt = PromptTemplate(
       input_variables=["question"],
       template="Answer this question concisely: {question}",
   )

   memory = ConversationBufferMemory()
   chain = LLMChain(prompt=prompt, llm=OpenAI(), memory=memory)

   # First question
   print(chain.run(question="What is Python?"))
   # "Python is a programming language"

   # Follow-up question — the prompt now includes the first exchange
   print(chain.run(question="Who created it?"))
   # "Python was created by Guido van Rossum"

   # Inspect memory
   print(memory.load_context())
   # Human: What is Python?
   # AI: Python is a programming language
   # Human: Who created it?
   # AI: Python was created by Guido van Rossum

ConversationBufferWindowMemory
-------------------------------

Limit history to the last 2 rounds:

.. code-block:: python

   from langchain import ConversationBufferWindowMemory

   memory = ConversationBufferWindowMemory(k=2)
   chain = LLMChain(prompt=prompt, llm=OpenAI(), memory=memory)

   # After 5 rounds, only the last 2 are included in the prompt
   for i in range(5):
       chain.run(question=f"Question {i+1}")

   print(memory.load_context())  # Only last 2 rounds