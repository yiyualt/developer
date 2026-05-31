
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
print(agent.run("Calculate 42*7 and email the result to alice@example.com"))