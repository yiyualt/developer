"""Middleware — hooks into the Agent execution loop.

Middleware sits between the Agent's reasoning and tool execution. Before
a tool is called, each registered middleware's ``before_tool`` hook runs.
Middleware can approve, reject, or modify tool calls — enabling
human-in-the-loop, audit logging, rate limiting, and other cross-cutting
behaviors without modifying Agent internals.
"""

import re
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


class PIIMiddleware(Middleware):
    """Detect and redact personally identifiable information in tool inputs.

    Before a tool executes, PIIMiddleware scans the input string for
    sensitive data patterns and replaces them according to the chosen
    strategy. The tool never sees the original sensitive data.

    Args:
        pii_type: Type of PII to detect. Supported: ``"email"``,
            ``"credit_card"``.
        strategy: How to handle detected PII.
            - ``"redact"``: Replace entire match with ``[REDACTED]``.
            - ``"mask"``: Preserve last 4 characters, replace earlier
              characters with ``*``.

    Examples:
        >>> agent = Agent(
        ...     llm=llm, tools=[send_email],
        ...     middleware=[
        ...         PIIMiddleware("email", strategy="redact"),
        ...         PIIMiddleware("credit_card", strategy="mask"),
        ...     ],
        ... )
        >>> agent.run("Send report to alice@example.com")
        # send_email receives "Send report to [REDACTED]"
    """

    PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    }

    def __init__(self, pii_type: str, strategy: str = "redact") -> None:
        if pii_type not in self.PATTERNS:
            raise ValueError(
                f"Unknown PII type '{pii_type}'. "
                f"Supported: {list(self.PATTERNS.keys())}"
            )
        if strategy not in ("redact", "mask"):
            raise ValueError(
                f"Unknown strategy '{strategy}'. Supported: redact, mask"
            )
        self.pii_type = pii_type
        self.strategy = strategy
        self._pattern = re.compile(self.PATTERNS[pii_type])

    def before_tool(self, tool_name: str, tool_input: str) -> tuple:
        """Scan input and apply the chosen PII strategy."""
        if self.strategy == "redact":
            cleaned = self._pattern.sub("[REDACTED]", tool_input)
        else:
            cleaned = self._pattern.sub(self._mask, tool_input)
        return (True, cleaned)

    def _mask(self, match: re.Match) -> str:
        """Preserve last 4 characters, replace the rest with *."""
        text = match.group()
        if len(text) > 4:
            return "*" * (len(text) - 4) + text[-4:]
        return "****"
