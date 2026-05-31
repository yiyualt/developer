"""ConversationalAgent — a message-native Agent for multi-turn dialogue.

Unlike the original Agent which works with plain strings, ConversationalAgent
uses typed messages (SystemMessage, HumanMessage, AIMessage) throughout:
system prompt is a SystemMessage, conversation history comes from
Memory.load_messages(), and LLM calls use generate_messages() so roles
are correctly preserved.

This is where Chat Model, Memory↔Chat, Callbacks, and Async converge
into a single Agent.
"""

import asyncio
from typing import Callable, Dict, List, Optional

from langchain.agents.output_parser import (
    AgentAction,
    AgentFallback,
    AgentFinish,
    parse_agent_output,
)
from langchain.callbacks.base import CallbackHandler
from langchain.callbacks.mixin import CallbackMixin
from langchain.llms.base import LLM
from langchain.memory.base import Memory
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.tools.base import Tool

MESSAGE_PROMPT = """You are an agent that uses ReAct (Reasoning + Acting) to answer questions.

You have access to the following tools:
{tool_descriptions}

Use the following format:
Thought: your reasoning about what to do
Action: tool_name[action_input]
OR
Thought: your reasoning
Final Answer: your final answer to the question"""


class ConversationalAgent(CallbackMixin):
    """A message-native Agent for multi-turn conversation.

    ConversationalAgent differs from Agent in one fundamental way:
    everything is a typed message, not a string. The system prompt is a
    SystemMessage, history comes from Memory.load_messages(), and LLM
    calls use generate_messages() — preserving roles throughout.

    Args:
        llm: LLM instance (must support generate_messages, e.g. OpenAI).
        tools: List of Tool instances available to the agent.
        system_message: The system prompt string.
        memory: Optional Memory instance for conversation history.
        max_iterations: Max ReAct iterations. Default is 5.
        callbacks: Optional list of CallbackHandler instances.
        description: Optional description for AgentTool wrapping.

    Examples:
        >>> agent = ConversationalAgent(
        ...     llm=OpenAI(), tools=[CalculatorTool()],
        ...     system_message="You are a helpful math tutor.",
        ...     memory=ConversationBufferMemory(),
        ... )
        >>> agent.run("What is the derivative of x²?")
        '2x'
        >>> agent.run("What about x³?")  # remembers previous context
        '3x²'
    """

    def __init__(
        self,
        llm: LLM,
        tools: List[Tool],
        system_message: str = "You are a helpful assistant.",
        memory: Optional[Memory] = None,
        max_iterations: int = 5,
        callbacks: Optional[List[CallbackHandler]] = None,
        description: str = "",
        approver: Optional[Callable[[str, str], tuple]] = None,
    ) -> None:
        self.llm = llm
        self.tools = tools
        self.system_message = system_message
        self.memory = memory
        self.max_iterations = max_iterations
        self.callbacks = callbacks or []
        self.description = description
        self.approver = approver
        self._tool_map = {t.name: t for t in tools}

    def _build_tool_descriptions(self) -> str:
        lines = [f"- {t.name}: {t.description}" for t in self.tools]
        return "\n".join(lines)

    def _execute_tool(self, action: AgentAction) -> str:
        tool = self._tool_map.get(action.tool)
        if tool is None:
            return f"Error: tool '{action.tool}' not found"
        if tool.requires_approval and self.approver:
            approved, modified = self.approver(action.tool, action.tool_input)
            if not approved:
                return f"Tool '{action.tool}' rejected by human reviewer."
            action.tool_input = modified
        return tool.run(action.tool_input)

    def _build_messages(self, question: str) -> List:
        """Build the base message list: system + history + question."""
        messages: List = [SystemMessage(content=self.system_message)]
        if self.memory:
            messages.extend(self.memory.load_messages())
        messages.append(HumanMessage(content=question))
        return messages

    def _build_react_prompt(self, scratchpad: str) -> str:
        """Build the ReAct instruction prompt with scratchpad."""
        prompt = MESSAGE_PROMPT.format(
            tool_descriptions=self._build_tool_descriptions(),
        )
        if scratchpad:
            prompt += f"\n{scratchpad}"
        return prompt

    async def _react_loop(
        self, question: str, use_async: bool
    ) -> Dict:
        """Shared ReAct loop — sync or async depending on use_async.

        The only difference between sync and async is which LLM method
        is called: ``generate_messages()`` vs ``agenerate_messages()``.
        """
        try:
            base_messages = self._build_messages(question)
            scratchpad = ""
            log = []

            for i in range(self.max_iterations):
                react_prompt = self._build_react_prompt(scratchpad)
                call_messages = base_messages + [HumanMessage(content=react_prompt)]

                if use_async:
                    response = (await self.llm.agenerate_messages([call_messages]))[0]
                else:
                    response = self.llm.generate_messages([call_messages])[0]

                parsed = parse_agent_output(response)

                if isinstance(parsed, AgentFinish):
                    log.append({
                        "thought": parsed.thought,
                        "final_answer": parsed.final_answer,
                    })
                    self._fire("on_agent_finish", final_answer=parsed.final_answer)
                    if self.memory:
                        self.memory.save_context(
                            {"question": question},
                            {"text": parsed.final_answer},
                        )
                    return {"answer": parsed.final_answer, "log": log}

                if isinstance(parsed, AgentAction):
                    self._fire("on_agent_action", action=f"{parsed.tool}[{parsed.tool_input}]")
                    observation = self._execute_tool(parsed)
                    entry = {
                        "thought": parsed.thought,
                        "action": f"{parsed.tool}[{parsed.tool_input}]",
                        "observation": observation,
                    }
                    log.append(entry)
                    scratchpad += (
                        f"\nThought: {parsed.thought}\n"
                        f"Action: {parsed.tool}[{parsed.tool_input}]\n"
                        f"Observation: {observation}\n"
                    )
                    continue

                log.append({"thought": parsed.thought})
                scratchpad += f"\nThought: {parsed.thought}\n"
                continue

            last_thought = log[-1]["thought"] if log else question
            if self.memory:
                self.memory.save_context(
                    {"question": question}, {"text": last_thought}
                )
            return {"answer": last_thought, "log": log}
        except Exception as e:
            self._fire("on_error", error=e)
            raise

    def _run_loop(self, question: str) -> Dict:
        return asyncio.run(self._react_loop(question, use_async=False))

    async def _arun_loop(self, question: str) -> Dict:
        return await self._react_loop(question, use_async=True)

    def run(self, question: str) -> str:
        return self._run_loop(question)["answer"]

    def run_with_log(self, question: str) -> Dict:
        return self._run_loop(question)

    async def apply_async(self, questions: List[str]) -> List[str]:
        async def _run_one(q):
            result = await self._arun_loop(q)
            return result["answer"]
        return await asyncio.gather(*[_run_one(q) for q in questions])
