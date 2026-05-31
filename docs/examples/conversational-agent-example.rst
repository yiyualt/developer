Conversational Agent Example
============================

Message-native multi-turn dialogue with SystemMessage, Memory, and tools.

Basic conversation
-------------------

.. code-block:: python

   from langchain import ConversationalAgent, OpenAI, CalculatorTool

   agent = ConversationalAgent(
       llm=OpenAI(),
       tools=[CalculatorTool()],
       system_message="You are a helpful math tutor. Answer concisely.",
   )

   answer = agent.run("What is the derivative of x²?")
   print(answer)  # "2x"

Multi-turn with memory
-----------------------

.. code-block:: python

   from langchain import (
       ConversationalAgent, OpenAI,
       ConversationBufferMemory, CalculatorTool,
   )

   agent = ConversationalAgent(
       llm=OpenAI(),
       tools=[CalculatorTool()],
       system_message="You are a helpful math tutor.",
       memory=ConversationBufferMemory(),
   )

   # Turn 1
   print(agent.run("The derivative of x² is 2x."))
   # Turn 2 — agent remembers the context
   print(agent.run("What is it at x=3?"))
   # "At x=3, the derivative of x² is 6."

Inspecting message history
---------------------------

.. code-block:: python

   result = agent.run_with_log("What is 2+3?")
   print(f"Answer: {result['answer']}")
   for step in result["log"]:
       print(step)

With async
-----------

.. code-block:: python

   import asyncio

   questions = [
       "What is 10 * 5?",
       "What is 99 + 1?",
   ]
   answers = asyncio.run(agent.apply_async(questions))
   print(answers)  # ["50", "100"]
