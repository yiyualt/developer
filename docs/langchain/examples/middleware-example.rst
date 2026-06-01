Middleware Examples
==================

Require human approval before executing specific tools — configured
entirely on middleware, not on tools.

Basic usage
-----------

.. code-block:: python

   from langchain import Agent, OpenAI, CalculatorTool
   from langchain.agents.middleware import HumanInTheLoopMiddleware
   from langchain.tools.base import Tool

   class SendEmailTool(Tool):
       name = "send_email"
       description = "Sends an email. Input: recipient and body."

       def _run(self, input: str) -> str:
           return f"Email sent to {input}"

   def terminal_approver(tool_name, arguments):
       print(f"Agent wants to call: {tool_name}[{arguments}]")
       answer = input("Approve? [y/N/modified_input]: ")
       if answer.lower() == "y":
           return True, arguments
       elif answer:
           return True, answer
       return False, arguments

   hitl = HumanInTheLoopMiddleware(
       interrupt_on={"send_email": True},
       approver=terminal_approver,
   )

   llm = OpenAI()
   agent = Agent(
       llm=llm,
       tools=[CalculatorTool(), SendEmailTool()],
       middleware=[hitl],
   )
   # Calculator runs freely (not in interrupt_on)
   # SendEmailTool pauses for human confirmation
   agent.run("Calculate 42*7 and email the result to alice@example.com")

Per-tool configuration
----------------------

.. code-block:: python

   hitl = HumanInTheLoopMiddleware(
       interrupt_on={
           "write_db": True,      # always interrupt
           "read_db": False,      # never interrupt (explicit)
           "send_email": True,
           # calculator not listed → never interrupted
       },
       approver=terminal_approver,
   )
   agent = Agent(
       llm=llm, tools=[CalculatorTool(), SendEmailTool()], middleware=[hitl]
   )

Audit log (always-approve + record)
------------------------------------

.. code-block:: python

   audit_log = []

   def logging_approver(tool_name, arguments):
       audit_log.append((tool_name, arguments))
       return True, arguments

   hitl = HumanInTheLoopMiddleware(
       interrupt_on={"send_email": True},
       approver=logging_approver,
   )
   agent = Agent(
       llm=llm, tools=[CalculatorTool(), SendEmailTool()], middleware=[hitl]
   )
   agent.run("Send the weekly report to boss@example.com")
   print("Audit log:", audit_log)

PII detection
-------------

Detect and redact sensitive data before it reaches tools:

.. code-block:: python

   from langchain.agents.middleware import PIIMiddleware

   agent = Agent(
       llm=llm, tools=[SendEmailTool()],
       middleware=[
           PIIMiddleware("email", strategy="redact"),
           PIIMiddleware("credit_card", strategy="mask"),
       ],
   )
   agent.run("Send invoice to bob@example.com, card 4111-1111-1111-1111")
   # SendEmailTool receives:
   # "Send invoice to [REDACTED], card ************1111"

Runtime limits
--------------

Limit LLM and tool calls to prevent runaway loops:

.. code-block:: python

   from langchain.agents.middleware import (
       ModelCallLimitMiddleware, ToolCallLimitMiddleware,
   )

   agent = Agent(
       llm=llm, tools=[CalculatorTool(), SearchTool()],
       middleware=[
           ModelCallLimitMiddleware(max_calls=20),
           ToolCallLimitMiddleware(
               max_calls=10,
               per_tool={"calculator": 3, "search": 5},
           ),
       ],
   )
   agent.run("Research Python and calculate 42*7")
