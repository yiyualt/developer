"""Agent - ReAct (Reasoning + Acting) autonomous execution loop.

Agent executes a ReAct loop where the LLM alternates between
thinking (Thought) and acting (Action) until it produces a
Final Answer. Each Action invokes a Tool, and the Observation
is appended to the prompt for the next iteration.
"""

from typing import Dict, List, Optional

from langchain.agents.output_parser import (
    AgentAction,
    AgentFallback,
    AgentFinish,
    parse_agent_output,
)
from langchain.llms.base import LLM
from langchain.memory.base import Memory
from langchain.tools.base import Tool

REACT_PROMPT_TEMPLATE = """You are an agent that uses ReAct (Reasoning + Acting) to answer questions.

You have access to the following tools:
{tool_descriptions}

Use the following format:
Thought: your reasoning about what to do
Action: tool_name[action_input]
OR
Thought: your reasoning
Final Answer: your final answer to the question

Begin!

Question: {question}
{scratchpad}"""


class Agent:
    """ReAct Agent that autonomously selects and executes tools.

    Args:
        llm: An LLM instance for generating thoughts and actions.
        tools: A list of Tool instances available to the agent.
        max_iterations: Maximum number of ReAct loop iterations
            before terminating. Default is 5.

    Examples:
        Simple agent with calculator::

            >>> from langchain import Agent, OpenAI, CalculatorTool
            >>> agent = Agent(llm=OpenAI(), tools=[CalculatorTool()])
            >>> agent.run(question="What is 2 + 3?")
            '5'
    """

    def __init__(
        self,
        llm: LLM,
        tools: List[Tool],
        max_iterations: int = 5,
        memory: Optional[Memory] = None,
    ) -> None:
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations
        self.memory = memory
        self._tool_map = {t.name: t for t in tools}

    def _build_tool_descriptions(self) -> str:
        lines = [f"- {t.name}: {t.description}" for t in self.tools]
        return "\n".join(lines)

    def _build_prompt(self, question: str, scratchpad: str) -> str:
        return REACT_PROMPT_TEMPLATE.format(
            tool_descriptions=self._build_tool_descriptions(),
            question=question,
            scratchpad=scratchpad,
        )

    def _execute_tool(self, action: AgentAction) -> str:
        tool = self._tool_map.get(action.tool)
        if tool is None:
            return f"Error: tool '{action.tool}' not found. Available: {list(self._tool_map.keys())}"
        return tool.run(action.tool_input)

    def run(self, question: str) -> str:
        """Execute the ReAct loop and return the Final Answer.

        Args:
            question: The question to answer.

        Returns:
            The Final Answer string from the LLM, or the last
            Thought if max_iterations is reached.
        """
        result = self._run_loop(question)
        return result["answer"]

    def run_with_log(self, question: str) -> Dict:
        """Execute the ReAct loop and return answer + full log.

        Args:
            question: The question to answer.

        Returns:
            A dict with "answer" (str) and "log" (list of dicts),
            each containing thought, action/observation, or
            final_answer from each iteration.
        """
        return self._run_loop(question)

    def _run_loop(self, question: str) -> Dict:
        scratchpad = ""
        if self.memory:
            history = self.memory.load_context()
            if history:
                scratchpad = history + "\n"
        log = []

        for i in range(self.max_iterations):
            prompt = self._build_prompt(question, scratchpad)
            response = self.llm.generate([prompt])[0]
            parsed = parse_agent_output(response)

            if isinstance(parsed, AgentFinish):
                log.append({"thought": parsed.thought, "final_answer": parsed.final_answer})
                if self.memory:
                    self.memory.save_context({"question": question}, {"text": parsed.final_answer})
                return {"answer": parsed.final_answer, "log": log}

            if isinstance(parsed, AgentAction):
                observation = self._execute_tool(parsed)
                entry = {
                    "thought": parsed.thought,
                    "action": f"{parsed.tool}[{parsed.tool_input}]",
                    "observation": observation,
                }
                log.append(entry)
                scratchpad += f"\nThought: {parsed.thought}\nAction: {parsed.tool}[{parsed.tool_input}]\nObservation: {observation}\n"
                continue

            # AgentFallback — treat as thought, continue without tool
            log.append({"thought": parsed.thought})
            scratchpad += f"\nThought: {parsed.thought}\n"
            continue

        # Max iterations reached — return last thought as answer
        last_thought = log[-1]["thought"] if log else question

        if self.memory:
            self.memory.save_context({"question": question}, {"text": last_thought})

        return {"answer": last_thought, "log": log}