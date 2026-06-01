Self-Correction Example
========================

Wrap any Agent with ``SelfCorrectingAgent`` to automatically validate
output and retry on failure.

Basic usage
-----------

.. code-block:: python

   from langchain import (
       Agent, OpenAI,
       LLMCorrector, SelfCorrectingAgent,
       CalculatorTool,
   )

   llm = OpenAI()

   # Create a regular Agent
   agent = Agent(llm=llm, tools=[CalculatorTool()])

   # Wrap with self-correction
   corrector = LLMCorrector(llm=llm)
   sc_agent = SelfCorrectingAgent(agent=agent, corrector=corrector)

   answer = sc_agent.run("What is the derivative of x² at x=3?")
   print(answer)

Inspecting the correction log
------------------------------

Use ``run_with_log`` to see how many attempts were made:

.. code-block:: python

   result = sc_agent.run_with_log("What is 2+2?")
   print(f"Attempts: {len(result['attempts'])}")
   for i, a in enumerate(result["attempts"]):
       status = "✓" if a["passed"] else "✗"
       print(f"  {status} Attempt {i+1}: {a['answer']}")
   print(f"Final: {result['final_answer']}")

Custom max_retries
-------------------

.. code-block:: python

   sc_agent = SelfCorrectingAgent(
       agent=agent,
       corrector=LLMCorrector(llm=llm),
       max_retries=5,  # default is 3
   )

With PlanAndExecuteAgent
-------------------------

SelfCorrectingAgent wraps any Agent, including PlanAndExecute:

.. code-block:: python

   from langchain import PlanAndExecuteAgent

   plan_agent = PlanAndExecuteAgent(llm=llm, tools=[SearchTool()])
   sc_agent = SelfCorrectingAgent(
       agent=plan_agent,
       corrector=LLMCorrector(llm=llm),
   )
   result = sc_agent.run("Research and summarize Python's history")
