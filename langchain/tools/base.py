"""Tool - abstract base class for Agent tools.

A Tool defines an interface that the Agent can invoke during a ReAct
loop. Each Tool has a unique name, a description (used in the ReAct
prompt to tell the LLM what tools are available), and a run method.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from langchain.callbacks.base import CallbackHandler


class Tool(ABC):
    """Abstract base class for Agent tools.

    Every Tool exposes three attributes: name (unique identifier),
    description (short text for the ReAct prompt), and run (the
    execution method that takes a string input and returns a string
    result or error message).

    Subclass Tool to create custom tools for the Agent.
    """

    name: str = ""
    description: str = ""

    def __init__(self, callbacks: Optional[List[CallbackHandler]] = None) -> None:
        self.callbacks = callbacks or []

    def _fire(self, event: str, **kwargs) -> None:
        """Invoke an event on all registered callback handlers."""
        for handler in self.callbacks:
            getattr(handler, event)(**kwargs)

    @abstractmethod
    def _run(self, input: str) -> str:
        """Internal execution method — subclasses implement this.

        Args:
            input: The input string for the tool.

        Returns:
            A string result. On error, return an error message string.
        """
        ...

    def run(self, input: str) -> str:
        """Execute the tool with the given input and return the result.

        Fires on_tool_start before execution and on_tool_end after
        completion. If execution raises an exception, fires on_error
        and re-raises.

        Args:
            input: The input string for the tool.

        Returns:
            A string result. On error, return an error message string.
        """
        self._fire("on_tool_start", tool_name=self.name, tool_input=input)
        try:
            result = self._run(input)
            self._fire("on_tool_end", output=result)
            return result
        except Exception as e:
            self._fire("on_error", error=e)
            raise