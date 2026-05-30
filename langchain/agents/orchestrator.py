"""Agent orchestration patterns — pre-built coordination for multi-agent systems.

Where AgentTool provides the *mechanism* for agent composition, this module
provides the *patterns* — common ways to coordinate multiple agents without
writing boilerplate every time.

Two patterns:
- **MultiAgentOrchestrator**: Route a question to the most appropriate specialist.
- **SequentialAgentChain**: Pipe output from one agent as input to the next.
"""

from typing import Dict, List, Optional

from langchain.agents.agent import Agent
from langchain.agents.tool import AgentTool
from langchain.callbacks.base import CallbackHandler
from langchain.callbacks.mixin import CallbackMixin
from langchain.llms.base import LLM


class MultiAgentOrchestrator(CallbackMixin):
    """Route a question to the most appropriate specialist agent.

    MultiAgentOrchestrator wraps each specialist in an AgentTool,
    creates an internal orchestrator Agent that sees all specialists
    as tools, and uses ReAct reasoning to decide which specialist
    (or combination of specialists) to call.

    This is the "router" pattern for multi-agent systems — one
    coordinator, many specialists.

    Args:
        llm: LLM instance used by the orchestrator Agent.
        specialists: List of Agent instances, each specialized in
            a different domain. Each Agent's ``description`` is
            used to inform the orchestrator about expertise.
        max_iterations: Max ReAct iterations for the orchestrator.
            Default is 5.
        callbacks: Optional list of CallbackHandler instances.

    Examples:
        Math + creative orchestration::

            >>> orch = MultiAgentOrchestrator(
            ...     llm=llm,
            ...     specialists=[math_agent, creative_agent],
            ... )
            >>> orch.run("What is 42*7? Write a poem about it.")
            '294. Here is a poem: ...'
    """

    def __init__(
        self,
        llm: LLM,
        specialists: List[Agent],
        max_iterations: int = 5,
        callbacks: Optional[List[CallbackHandler]] = None,
    ) -> None:
        self.callbacks = callbacks or []
        self.llm = llm
        self.specialists = specialists
        self.max_iterations = max_iterations

        # Wrap each specialist as a Tool
        self.tools: List[AgentTool] = []
        for i, agent in enumerate(specialists):
            name = f"specialist_{i}"
            tool = AgentTool(name=name, agent=agent)
            self.tools.append(tool)

        # Create the internal orchestrator Agent
        self._orchestrator = Agent(
            llm=llm,
            tools=list(self.tools),
            max_iterations=max_iterations,
            callbacks=self.callbacks,
            description="Orchestrator agent that delegates questions to specialist agents",
        )

    def run(self, question: str) -> str:
        """Route a question and return the final answer.

        Args:
            question: The question to answer.

        Returns:
            The final answer string.
        """
        return self._orchestrator.run(question=question)

    def run_with_log(self, question: str) -> Dict:
        """Route a question and return the full execution log.

        Args:
            question: The question to answer.

        Returns:
            Dict with:
            - ``specialists``: list of specialist names
            - ``log``: the orchestrator Agent's full ReAct log
            - ``final_answer``: the final answer string
        """
        result = self._orchestrator.run_with_log(question=question)
        return {
            "specialists": [t.name for t in self.tools],
            "log": result["log"],
            "final_answer": result["answer"],
        }


class SequentialAgentChain(CallbackMixin):
    """Execute agents in sequence, piping output as input.

    SequentialAgentChain runs agents one after another: Agent₁
    processes the question, Agent₂ processes Agent₁'s output,
    Agent₃ processes Agent₂'s output, and so on. The final agent's
    output is the chain's result.

    Each agent is a full ReAct agent — it can use tools, reason
    through multiple steps, and produce any output. The next agent
    receives that output as its ``question``.

    Args:
        agents: List of Agent instances in execution order.
        callbacks: Optional list of CallbackHandler instances.

    Examples:
        Plan → Execute → Review pipeline::

            >>> pipeline = SequentialAgentChain([
            ...     planner_agent,
            ...     executor_agent,
            ...     reviewer_agent,
            ... ])
            >>> pipeline.run("Build a blog website")
            'The blog has been built and reviewed. Here is...'
    """

    def __init__(
        self,
        agents: List[Agent],
        callbacks: Optional[List[CallbackHandler]] = None,
    ) -> None:
        self.agents = agents
        self.callbacks = callbacks or []
        # Merge chain callbacks into each agent
        if callbacks:
            for agent in self.agents:
                agent.callbacks = list(
                    {id(h): h for h in agent.callbacks + list(callbacks)}.values()
                )

    def run(self, question: str) -> str:
        """Execute agents in sequence and return the final output.

        Args:
            question: The initial question or task.

        Returns:
            The output of the last agent in the chain.
        """
        result = question
        for agent in self.agents:
            result = agent.run(question=result)
        return result

    def run_with_log(self, question: str) -> Dict:
        """Execute in sequence and return the full log.

        Args:
            question: The initial question or task.

        Returns:
            Dict with:
            - ``steps``: list of dicts with ``agent``, ``input``,
              ``output``, and ``log`` keys
            - ``final_answer``: the last agent's output
        """
        steps = []
        current_input = question
        for i, agent in enumerate(self.agents):
            name = getattr(agent, "description", f"agent_{i}") or f"agent_{i}"
            result = agent.run_with_log(question=current_input)
            steps.append({
                "agent": name,
                "input": current_input,
                "output": result["answer"],
                "log": result["log"],
            })
            current_input = result["answer"]

        return {
            "steps": steps,
            "final_answer": current_input,
        }
