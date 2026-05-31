Human-in-the-Loop Example
=========================

Require human approval before executing sensitive tools — built into
Agent, no middleware wrapper needed.

Basic usage
-----------

.. code-block:: python

   from langchain import Agent, OpenAI, CalculatorTool
   from langchain.tools.base import Tool

   # Tool declares it needs approval
   class SendEmailTool(Tool):
       name = "send_email"
       description = "Sends an email. Input: recipient and body."
       requires_approval = True

       def _run(self, input: str) -> str:
           return f"Email sent to {input}"

   # Terminal-based approver
   def terminal_approver(tool_name, arguments):
       print(f"Agent wants to call: {tool_name}[{arguments}]")
       answer = input("Approve? [y/N/modified_input]: ")
       if answer.lower() == "y":
           return True, arguments
       elif answer:
           return True, answer
       return False, arguments

   llm = OpenAI()
   agent = Agent(
       llm=llm,
       tools=[CalculatorTool(), SendEmailTool()],
       approver=terminal_approver,
   )
   # Calculator runs without approval (requires_approval=False)
   # SendEmailTool pauses for human confirmation
   agent.run("Calculate 42*7 and email the result to alice@example.com")

Per-tool declaration
--------------------

Each tool declares whether it needs approval:

.. code-block:: python

   from langchain import Agent
   from langchain.tools.base import Tool

   class ReadTool(Tool):
       name = "read_db"
       description = "Read data from database"
       requires_approval = False

       def _run(self, input: str) -> str:
           return f"Read: {input}"

   class WriteTool(Tool):
       name = "write_db"
       description = "Write data to database"
       requires_approval = True

       def _run(self, input: str) -> str:
           return f"Wrote: {input}"

   def ask_user(tool_name, arguments):
       answer = input(f"Allow {tool_name}[{arguments}]? [y/N]: ")
       return (answer.lower() == "y", arguments)

   agent = Agent(llm=llm, tools=[ReadTool(), WriteTool()], approver=ask_user)
   agent.run("Read the user table then update the admin record")
   # ReadTool runs automatically, WriteTool pauses for approval

Audit log (always-approve + record)
------------------------------------

.. code-block:: python

   from langchain import Agent
   from langchain.tools.calculator import CalculatorTool

   audit_log = []

   def logging_approver(tool_name, arguments):
       audit_log.append((tool_name, arguments))
       return True, arguments

   agent = Agent(llm=llm, tools=[CalculatorTool()], approver=logging_approver)
   agent.run("What is 15 * 7?")
   print("Audit log:", audit_log)
   # Output: Audit log: [('calculator', '15*7')]
