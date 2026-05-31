Function Calling Example
========================

Native tool calling via API — no string parsing needed.

Basic usage
-----------

.. code-block:: python

   from langchain import FunctionCallingAgent, OpenAI, CalculatorTool

   llm = OpenAI()
   agent = FunctionCallingAgent(
       llm=llm,
       tools=[CalculatorTool()],
       system_message="You are a helpful math tutor.",
   )

   answer = agent.run("What is 15 * 7 + 3?")
   print(answer)  # "108"

With multiple tools
-------------------

.. code-block:: python

   from langchain import FunctionCallingAgent, OpenAI, CalculatorTool, SearchTool

   agent = FunctionCallingAgent(
       llm=llm,
       tools=[CalculatorTool(), SearchTool()],
       system_message="You are a research assistant.",
   )

   answer = agent.run(
       "What is the population of Tokyo? Then calculate 10% of it."
   )

With memory
-----------

.. code-block:: python

   from langchain import (
       FunctionCallingAgent, OpenAI,
       ConversationBufferMemory, CalculatorTool,
   )

   agent = FunctionCallingAgent(
       llm=llm,
       tools=[CalculatorTool()],
       memory=ConversationBufferMemory(),
   )
   agent.run("My name is Alice.")
   agent.run("What's my name?")  # knows from memory

How it differs from Agent
--------------------------

The original Agent prompts the LLM to output ``Action: tool[input]`` strings,
then parses them with regex. FunctionCallingAgent sends tool JSON Schemas to
the API and receives structured ``tool_calls`` — no parsing, no format errors.
