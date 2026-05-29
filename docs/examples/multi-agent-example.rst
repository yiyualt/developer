Multi-Agent Example
====================

This example demonstrates Agent composition — wrapping specialist
Agents as Tools and coordinating them through an orchestrator Agent.

Two specialist agents
---------------------

Create two specialist agents, each with focused tools and skills:

.. code-block:: python

   from langchain import (
       Agent, OpenAI,
       CalculatorTool, SearchTool,
       AgentTool
   )

   llm = OpenAI()

   math_agent = Agent(
       llm=llm,
       tools=[CalculatorTool()],
       description="Solves math problems using a calculator",
   )

   research_agent = Agent(
       llm=llm,
       tools=[SearchTool()],
       description="Searches the web for factual information",
   )

Wrapping agents as tools
-------------------------

Wrap each specialist in an AgentTool so they can be used by
another Agent:

.. code-block:: python

   math_tool = AgentTool(name="math_expert", agent=math_agent)
   research_tool = AgentTool(name="researcher", agent=research_agent)

   for tool in [math_tool, research_tool]:
       print(f"{tool.name}: {tool.description}")
   # math_expert: Solves math problems using a calculator
   # researcher: Searches the web for factual information

Orchestrator agent
-------------------

Create an orchestrator Agent that can delegate to either specialist:

.. code-block:: python

   orchestrator = Agent(
       llm=llm,
       tools=[math_tool, research_tool],
   )

   # The orchestrator decides which specialist to call
   answer = orchestrator.run(
       question="What is the population of Tokyo? Then calculate 10% of it."
   )
   print(answer)

Specialist agent with custom description
-----------------------------------------

You can override the description when wrapping — useful when the same
Agent needs different descriptions in different contexts:

.. code-block:: python

   # Override the agent's own description with a context-specific one
   tool = AgentTool(
       name="math_expert",
       agent=math_agent,
       description="Handles arithmetic and numeric calculations only"
   )
   print(tool.description)
   # "Handles arithmetic and numeric calculations only"

Mixing AgentTools with regular Tools
--------------------------------------

AgentTool IS-A Tool, so you can freely mix it with regular tools:

.. code-block:: python

   orchestrator = Agent(
       llm=llm,
       tools=[
           CalculatorTool(),                # regular tool
           SearchTool(),                    # regular tool
           AgentTool(                       # specialist agent as tool
               name="math_expert",
               agent=math_agent,
           ),
           AgentTool(                       # another specialist
               name="researcher",
               agent=research_agent,
           ),
       ],
   )

   # The orchestrator can use any tool based on the question
   result = orchestrator.run_with_log(
       question="Research the GDP of France and convert it to scientific notation"
   )
   for step in result["log"]:
       print(step)
