Plan-and-Execute Example
==========================

This example demonstrates PlanAndExecuteAgent — an agent that decomposes
complex goals into ordered plans and executes them step by step.

Simple goal without tools
--------------------------

.. code-block:: python

   from langchain import PlanAndExecuteAgent, OpenAI

   llm = OpenAI()
   agent = PlanAndExecuteAgent(llm=llm)

   result = agent.run(goal="Write a 3-sentence introduction to Python")
   print(result)

Inspecting the plan and execution log
--------------------------------------

Use ``run_with_log()`` to see the plan and each step's result:

.. code-block:: python

   log = agent.run_with_log(goal="Write a 2-sentence summary of recursion")
   print("Plan:")
   for i, step in enumerate(log["plan"], 1):
       print(f"  {i}. {step}")

   print("\nExecution:")
   for s in log["steps"]:
       print(f"  Step {s['step_num']}: {s['step']}")
       print(f"  Result: {s['result'][:100]}...")
       print()

   print(f"Final: {log['final_answer']}")

Goal with tools for step execution
-----------------------------------

Provide tools so each step can use Search, Calculator, or even
specialist Agents:

.. code-block:: python

   from langchain import PlanAndExecuteAgent, OpenAI, SearchTool, CalculatorTool

   llm = OpenAI()
   agent = PlanAndExecuteAgent(
       llm=llm,
       tools=[SearchTool(), CalculatorTool()],
   )

   result = agent.run(
       goal="Research the GDP of France and Germany, then calculate the difference"
   )
   print(result)

Combining PlanAndExecute with AgentTool
-----------------------------------------

The real power: use AgentTool to let each step be executed by a
specialist Agent with its own tools and memory:

.. code-block:: python

   from langchain import (
       PlanAndExecuteAgent, Agent, AgentTool,
       OpenAI, SearchTool, CalculatorTool
   )

   llm = OpenAI()

   # Create specialist agents
   research_agent = Agent(
       llm=llm,
       tools=[SearchTool()],
       description="Expert researcher — finds factual information online",
   )

   math_agent = Agent(
       llm=llm,
       tools=[CalculatorTool()],
       description="Expert mathematician — performs calculations and analysis",
   )

   writing_agent = Agent(
       llm=llm,
       tools=[],
       description="Expert writer — synthesizes information into clear prose",
   )

   # Wrap as tools
   tools = [
       AgentTool(name="researcher", agent=research_agent),
       AgentTool(name="mathematician", agent=math_agent),
       AgentTool(name="writer", agent=writing_agent),
   ]

   # PlanAndExecute orchestrates the specialists
   orchestrator = PlanAndExecuteAgent(llm=llm, tools=tools)

   result = orchestrator.run_with_log(
       goal="Research Python's adoption in 2025, calculate year-over-year "
            "growth rate, and write a 2-paragraph summary"
   )

   print(f"Generated {len(result['plan'])} steps:")
   for step in result["plan"]:
       print(f"  - {step}")

   print(f"\nFinal answer:\n{result['final_answer']}")

Limiting max steps
------------------

Prevent runaway plans with ``max_steps``:

.. code-block:: python

   agent = PlanAndExecuteAgent(llm=llm, max_steps=5)

   # Even if the LLM generates a 10-step plan, only 5 execute
   result = agent.run(goal="Explain how computers work")
