Agent Example
=============

This example demonstrates the ReAct Agent — an LLM that autonomously
chooses tools, observes results, and decides whether to continue
reasoning or give a final answer.

Using CalculatorTool
---------------------

.. code-block:: python

   from langchain import Agent, OpenAI, CalculatorTool

   llm = OpenAI()
   agent = Agent(llm=llm, tools=[CalculatorTool()])

   answer = agent.run(question="What is 15 * 7 + 3?")
   print(answer)  # "108"

Using multiple tools
---------------------

.. code-block:: python

   from langchain import Agent, OpenAI, CalculatorTool, SearchTool

   llm = OpenAI()
   agent = Agent(
       llm=llm,
       tools=[CalculatorTool(), SearchTool()],
   )

   # The agent decides which tool to use based on the question
   answer = agent.run(question="How many letters are in the word 'Python'?")

Creating tools with @tool
-------------------------

Instead of subclassing Tool, use the ``@tool`` decorator to convert
a function into a Tool with zero boilerplate:

.. code-block:: python

   from langchain import Agent, OpenAI, tool

   @tool
   def calculator(input: str) -> str:
       """Performs arithmetic calculations. Input: math expression like '2+3'"""
       try:
           return str(eval(input))
       except Exception as e:
           return f"Error: {e}"

   # The function is now a Tool instance
   print(calculator.name)        # "calculator"
   print(calculator.description) # "Performs arithmetic calculations..."

   agent = Agent(llm=OpenAI(), tools=[calculator])
   answer = agent.run(question="What is 15 * 7 + 3?")

With explicit name and description::

.. code-block:: python

   @tool(name="calc", description="Solves math problems using arithmetic")
   def calculator(input: str) -> str:
       return str(eval(input))

Retrieving execution log
-------------------------

Use ``run_with_log()`` to see every Thought, Action, and Observation:

.. code-block:: python

   result = agent.run_with_log(question="What is 2 + 3?")
   print(result["answer"])  # "5"
   for step in result["log"]:
       print(step)