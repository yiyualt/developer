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