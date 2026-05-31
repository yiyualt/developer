"""Middleware — hooks into the Agent execution loop.

Middleware sits between the Agent's reasoning and tool execution. Before
a tool is called, each registered middleware's ``before_tool`` hook runs.
Middleware can approve, reject, or modify tool calls — enabling
human-in-the-loop, audit logging, rate limiting, and other cross-cutting
behaviors without modifying Agent internals.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional


class Middleware(ABC):
    """Base class for Agent middleware hooks.

    Subclass and override ``before_tool`` to intercept tool execution.
    The default implementation passes through unchanged.
    """

    def before_tool(self, tool_name: str, tool_input: str) -> tuple:
        """Called before every tool execution.

        Args:
            tool_name: The name of the tool about to be called.
            tool_input: The input string for the tool.

        Returns:
            A tuple of ``(should_proceed: bool, modified_input: str)``.
            If ``should_proceed`` is False, the tool is skipped and the
            Agent receives a rejection message as the Observation.
        """
        return (True, tool_input)


class HumanInTheLoopMiddleware(Middleware):
    """Require human approval before executing specific tools.

    Configuration lives entirely on the middleware — tools don't need
    to know they're being intercepted.

    Args:
        interrupt_on: Dict mapping tool names to True/False/config dict.
            - ``True``: always interrupt for this tool.
            - ``False``: never interrupt.
            - ``{"allowed_decisions": ["approve","edit","reject"]}``:
              config dict (for future use, currently advisory).
            Tools not in the dict pass through without interruption.
        approver: Callable ``(tool_name, tool_input) ->
            (approved: bool, modified_input: str)``.
            Called when a tool requires approval.

    Examples:
        >>> middleware = HumanInTheLoopMiddleware(
        ...     interrupt_on={
        ...         "send_email": True,
        ...         "read_email": False,
        ...     },
        ...     approver=lambda name, args: (
        ...         input(f"{name}[{args}]? ").lower() == "y", args
        ...     ),
        ... )
        >>> agent = Agent(llm=llm, tools=[...], middleware=[middleware])
    """

    def __init__(
        self,
        interrupt_on: Optional[Dict[str, object]] = None,
        approver: Optional[Callable[[str, str], tuple]] = None,
    ) -> None:
        self.interrupt_on = interrupt_on or {}
        self.approver = approver

    def before_tool(self, tool_name: str, tool_input: str) -> tuple:
        """Check interrupt_on and call approver if needed."""
        if tool_name not in self.interrupt_on:
            return (True, tool_input)

        config = self.interrupt_on[tool_name]
        if config is False:
            return (True, tool_input)

        if self.approver is None:
            return (True, tool_input)

        approved, modified = self.approver(tool_name, tool_input)
        return (approved, modified)
