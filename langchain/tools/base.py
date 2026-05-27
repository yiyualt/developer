"""Tool - abstract base class for Agent tools.

A Tool defines an interface that the Agent can invoke during a ReAct
loop. Each Tool has a unique name, a description (used in the ReAct
prompt to tell the LLM what tools are available), and a run method.
"""

from abc import ABC, abstractmethod


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

    @abstractmethod
    def run(self, input: str) -> str:
        """Execute the tool with the given input and return the result.

        Args:
            input: The input string for the tool.

        Returns:
            A string result. On error, return an error message string.
        """
        ...