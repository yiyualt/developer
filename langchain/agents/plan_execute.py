"""PlanAndExecuteAgent — decompose complex goals into plans and execute step by step.

Unlike the ReAct Agent which answers a single question through iterative
reasoning, PlanAndExecuteAgent tackles complex *goals* that require
multiple distinct steps. It first decomposes the goal into an ordered plan,
then executes each step sequentially, passing context between steps.

This is the leap from "answer a question" to "achieve a goal".
"""

import re
from typing import Dict, List, Optional

from langchain.agents.agent import Agent
from langchain.callbacks.base import CallbackHandler
from langchain.callbacks.mixin import CallbackMixin
from langchain.llms.base import LLM
from langchain.tools.base import Tool

PLAN_PROMPT_TEMPLATE = """You are a planning agent. Given a goal, break it down into a numbered, ordered list of concrete steps to achieve that goal.

Each step should be a clear, actionable instruction. Output ONLY the numbered list, one step per line. Do not add any other text.

Goal: {goal}

Steps:
"""

EXECUTE_PROMPT_TEMPLATE = """You are an execution agent. Your task is to execute ONE specific step toward achieving a larger goal.

{context}

Execute the current step and return ONLY the result of your execution. Do not continue to other steps."""


class PlanAndExecuteAgent(CallbackMixin):
    """Agent that decomposes a goal into a plan and executes each step.

    PlanAndExecuteAgent uses a two-phase approach:
    1. **Plan**: The LLM breaks the goal into an ordered list of steps.
    2. **Execute**: Each step is executed in order, with the original
       goal, full plan, and all previous results provided as context.

    Args:
        llm: LLM instance for both planning and execution.
        tools: Optional list of Tool instances available during step
            execution. Each step can use these tools (including
            AgentTool for specialist delegation).
        max_steps: Maximum number of steps to execute. If the planner
            generates more, only the first max_steps are kept.
            Default is 10.

    Examples:
        Simple goal without tools::

            >>> agent = PlanAndExecuteAgent(llm=OpenAI())
            >>> agent.run(goal="Write a 3-sentence summary of Python")
            'Python is a versatile...'

        Goal with tools for research and calculation::

            >>> agent = PlanAndExecuteAgent(
            ...     llm=OpenAI(),
            ...     tools=[SearchTool(), CalculatorTool()],
            ... )
            >>> agent.run(goal="Research the GDP of France and calculate 10%")
    """

    def __init__(
        self,
        llm: LLM,
        tools: Optional[List[Tool]] = None,
        max_steps: int = 10,
        callbacks: Optional[List[CallbackHandler]] = None,
    ) -> None:
        self.llm = llm
        self.tools = tools or []
        self.max_steps = max_steps
        self.callbacks = callbacks or []

    def _parse_plan(self, response: str) -> List[str]:
        """Parse a numbered list of steps from LLM response.

        Supports common numbering formats:
        - "1. Step description"
        - "1) Step description"
        - Leading whitespace is stripped.

        Args:
            response: The raw LLM response string.

        Returns:
            A list of step description strings in order.
        """
        steps: List[str] = []
        for line in response.strip().split("\n"):
            line = line.strip()
            match = re.match(r"^(\d+)[\.\)]\s*(.+)", line)
            if match:
                step_text = match.group(2).strip()
                if step_text:
                    steps.append(step_text)
        return steps

    def _plan(self, goal: str) -> List[str]:
        """Generate a plan by asking the LLM to decompose the goal.

        Args:
            goal: The goal to decompose into steps.

        Returns:
            A list of step description strings, capped at ``max_steps``.
        """
        prompt = PLAN_PROMPT_TEMPLATE.format(goal=goal)
        response = self.llm.generate([prompt])[0]
        steps = self._parse_plan(response)
        return steps[: self.max_steps]

    def _build_execution_context(
        self,
        current_step: str,
        goal: str,
        plan: List[str],
        step_num: int,
        previous_results: List[Dict],
    ) -> str:
        """Build the prompt context for executing a single step.

        Includes the original goal, the full plan, all previous
        step results, and the current step to execute.

        Args:
            current_step: The description of the step being executed.
            goal: The original goal.
            plan: The full list of step descriptions.
            step_num: The 1-indexed number of the current step.
            previous_results: List of dicts with ``step`` and ``result``
                keys from previously executed steps.

        Returns:
            A formatted context string for the execution prompt.
        """
        lines = [f"Goal: {goal}", "", "Full Plan:"]
        for i, s in enumerate(plan, 1):
            marker = " → CURRENT" if i == step_num else ""
            lines.append(f"  {i}. {s}{marker}")

        if previous_results:
            lines.append("")
            lines.append("Previous Steps Completed:")
            for prev in previous_results:
                lines.append(f"  Step {prev['step_num']}: {prev['step']}")
                lines.append(f"  Result: {prev['result']}")
                lines.append("")

        lines.append("")
        lines.append(f"Execute Step {step_num}: {current_step}")
        return "\n".join(lines)

    def _execute_step(
        self,
        step: str,
        goal: str,
        plan: List[str],
        step_num: int,
        previous_results: List[Dict],
    ) -> str:
        """Execute a single step of the plan.

        If ``self.tools`` is non-empty, creates an Agent with those
        tools to execute the step (enabling ReAct reasoning per step).
        Otherwise, calls the LLM directly.

        Args:
            step: The step description to execute.
            goal: The original goal.
            plan: The full plan list.
            step_num: The 1-indexed number of this step.
            previous_results: List of previously completed step results.

        Returns:
            The execution result string for this step.
        """
        context = self._build_execution_context(
            step, goal, plan, step_num, previous_results
        )

        if self.tools:
            executor = Agent(llm=self.llm, tools=self.tools)
            return executor.run(question=context)
        else:
            prompt = EXECUTE_PROMPT_TEMPLATE.format(context=context)
            return self.llm.generate([prompt])[0]

    def run(self, goal: str) -> str:
        """Decompose a goal and execute the plan, returning the final answer.

        Args:
            goal: The goal to achieve.

        Returns:
            The result of the last step as a string.
        """
        result = self.run_with_log(goal)
        return result["final_answer"]

    def run_with_log(self, goal: str) -> Dict:
        """Decompose a goal and execute the plan, returning full details.

        Args:
            goal: The goal to achieve.

        Returns:
            A dict with:
            - ``plan``: list of step description strings
            - ``steps``: list of dicts with ``step_num``, ``step``,
              and ``result`` keys
            - ``final_answer``: the result of the last executed step
        """
        plan = self._plan(goal)
        steps_log: List[Dict] = []

        for i, step in enumerate(plan):
            step_num = i + 1
            result = self._execute_step(step, goal, plan, step_num, steps_log)
            steps_log.append({
                "step_num": step_num,
                "step": step,
                "result": result,
            })

        final_answer = steps_log[-1]["result"] if steps_log else ""
        return {
            "plan": plan,
            "steps": steps_log,
            "final_answer": final_answer,
        }
