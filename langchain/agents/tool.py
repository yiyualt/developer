"""AgentTool — wrap an Agent as a Tool for recursive Agent composition.

AgentTool makes an Agent look like a Tool, so one Agent can delegate
questions to another Agent. This provides recursive composability:
anywhere a Tool can be used, an Agent (wrapped in AgentTool) can be
used. The orchestrator Agent sees specialist Agents as just more tools
in its tool belt.
"""

from langchain.agents.agent import Agent
from langchain.tools.base import Tool


class AgentTool(Tool):
    """Wrap an Agent so it can be used as a Tool by another Agent.

    AgentTool IS-A Tool — it can be used anywhere a regular Tool is
    used. Internally, it delegates to ``agent.run(question=input)``.
    The wrapped Agent keeps its own ReAct loop, tools, and memory.

    Args:
        name: Unique tool name (appears in the orchestrator Agent's
            ReAct prompt).
        agent: The Agent instance to wrap.
        description: Optional description of what this tool does.
            Defaults to the wrapped Agent's ``description`` attribute,
            or a fallback string if neither is set.

    Examples:
        Wrapping a specialist agent::

            >>> math_agent = Agent(
            ...     llm=llm, tools=[CalculatorTool()],
            ...     description="Solves math problems"
            ... )
            >>> tool = AgentTool(name="math_expert", agent=math_agent)
            >>> tool.name
            'math_expert'
            >>> tool.description
            'Solves math problems'

        Using in an orchestrator Agent::

            >>> orchestrator = Agent(
            ...     llm=llm,
            ...     tools=[
            ...         CalculatorTool(),
            ...         AgentTool(name="researcher", agent=research_agent),
            ...     ]
            ... )
    """

    def __init__(
        self,
        name: str,
        agent: Agent,
        description: str = "",
    ) -> None:
        super().__init__()
        self.name = name
        self.agent = agent
        self.description = (
            description
            or agent.description
            or f"Delegates to {name} specialist agent"
        )

    def _run(self, input: str) -> str:
        """Delegate the question to the wrapped Agent.

        Args:
            input: The question string to pass to the wrapped Agent.

        Returns:
            The Agent's final answer, or an error message if
            execution fails.
        """
        try:
            return self.agent.run(question=input)
        except Exception as e:
            return f"Agent execution error: {e}"
