"""FunctionCallingAgent — native function calling without string parsing.

Current Agent parses "Action: calculator[2+3]" from LLM text using regex.
FunctionCallingAgent sends tool definitions to the API directly. The model
returns structured JSON tool_calls — no parsing, no format errors, no
"the LLM forgot the Action format."
"""

from typing import Dict, List, Optional

from langchain.callbacks.base import CallbackHandler
from langchain.callbacks.mixin import CallbackMixin
from langchain.llms.base import LLM
from langchain.memory.base import Memory
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools.base import Tool


class FunctionCallingAgent(CallbackMixin):
    """Agent that uses native function calling instead of string parsing.

    Instead of building a text prompt with tool descriptions and parsing
    "Action: tool[input]", this Agent sends tool JSON Schemas to the API
    and receives structured ``tool_calls`` in response.

    Args:
        llm: LLM instance (must support ``generate_with_tools``).
        tools: List of Tool instances.
        system_message: System prompt string. Default is helpful assistant.
        memory: Optional Memory instance.
        max_iterations: Max tool-calling rounds. Default is 5.
        callbacks: Optional list of CallbackHandler instances.

    Examples:
        >>> agent = FunctionCallingAgent(
        ...     llm=OpenAI(), tools=[CalculatorTool()],
        ...     system_message="You are a math tutor.",
        ... )
        >>> agent.run("What is 2+3?")
        '5'
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
    ) -> None:
        self.llm = llm
        self.tools = tools
        self.system_message = system_message
        self.memory = memory
        self.max_iterations = max_iterations
        self.callbacks = callbacks or []
        self.description = description
        self._tool_map = {t.name: t for t in tools}

    def _execute_tool(self, name: str, arguments: str) -> str:
        """Execute a tool call from the API response."""
        tool = self._tool_map.get(name)
        if tool is None:
            return f"Error: tool '{name}' not found"
        self._fire("on_tool_start", tool_name=name, tool_input=arguments)
        try:
            result = tool.run(arguments)
            self._fire("on_tool_end", output=result)
            return result
        except Exception as e:
            self._fire("on_error", error=e)
            return f"Error: {e}"

    def _run_loop(self, question: str) -> Dict:
        """Execute the function-calling loop."""
        try:
            messages: List = [SystemMessage(content=self.system_message)]
            if self.memory:
                messages.extend(self.memory.load_messages())
            messages.append(HumanMessage(content=question))

            log = []
            for i in range(self.max_iterations):
                response = self.llm.generate_with_tools(
                    [messages], self.tools
                )[0]

                # Model answered directly — final answer
                if response["content"] and not response["tool_calls"]:
                    answer = response["content"]
                    log.append({"final_answer": answer})
                    self._fire("on_agent_finish", final_answer=answer)
                    if self.memory:
                        self.memory.save_context(
                            {"question": question}, {"text": answer}
                        )
                    return {"answer": answer, "log": log}

                # Model requested tool calls — execute them
                if response["tool_calls"]:
                    for tc in response["tool_calls"]:
                        self._fire("on_agent_action",
                                   action=f"{tc['name']}[{tc['arguments']}]")
                        observation = self._execute_tool(
                            tc["name"], tc["arguments"]
                        )
                        log.append({
                            "tool_call": tc,
                            "observation": observation,
                        })
                        # Add tool result as context for next LLM call
                        messages.append(HumanMessage(
                            content=f"Tool [{tc['name']}] result: {observation}"
                        ))
                    continue

                # No content and no tool calls — shouldn't happen
                return {"answer": "", "log": log}

            last_answer = log[-1].get("observation", "") if log else ""
            return {"answer": last_answer, "log": log}
        except Exception as e:
            self._fire("on_error", error=e)
            raise

    def run(self, question: str) -> str:
        return self._run_loop(question)["answer"]

    def run_with_log(self, question: str) -> Dict:
        return self._run_loop(question)
