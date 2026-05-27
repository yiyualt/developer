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

Retrieving execution log
-------------------------

Use ``run_with_log()`` to see every Thought, Action, and Observation:

.. code-block:: python

   result = agent.run_with_log(question="What is 2 + 3?")
   print(result["answer"])  # "5"
   for step in result["log"]:
       print(step)