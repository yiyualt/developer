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

ConversationSummaryMemory
--------------------------

Compress long conversations into a concise summary:

.. code-block:: python

   from langchain import ConversationSummaryMemory, OpenAI

   # SummaryMemory needs an LLM for compression
   memory = ConversationSummaryMemory(llm=OpenAI())
   chain = LLMChain(prompt=prompt, llm=OpenAI(), memory=memory)

   # First few rounds — stored in buffer, no summary yet
   chain.run(question="What is Python?")
   chain.run(question="Who created it?")

   # After more rounds, older history is compressed into a summary
   chain.run(question="What is Python used for?")
   chain.run(question="What is the latest version?")

   # load_context() returns summary + recent buffer
   print(memory.load_context())
   # "The user asked about Python, a programming language created
   #  by Guido van Rossum. It's used for web development, data
   #  science, and scripting. The latest version is 3.13."
   # (followed by recent un-summarized rounds)

   # Summary keeps key facts even after many rounds
   chain.run(question="Is Python slow?")
   print(memory.load_context())
   # Summary still mentions "Python, created by Guido van Rossum"