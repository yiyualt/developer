"""Middleware — hooks into the Agent execution loop.

Middleware sits between the Agent's reasoning and tool execution. Before
a tool is called, each registered middleware's ``before_tool`` hook runs.
Middleware can approve, reject, or modify tool calls — enabling
human-in-the-loop, audit logging, rate limiting, and other cross-cutting
behaviors without modifying Agent internals.
"""

import re
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional


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

    def reset(self) -> None:
        """Reset any internal state between ``Agent.run()`` calls.

        Called at the start of each ``run()``. Override to clear
        counters, flush audit logs, or reset per-run state.
        """

    def before_llm(self, messages: list) -> list:
        """Called before every LLM call. Return transformed messages.

        Subclasses may override this to compress, filter, or augment
        the message list before it is sent to the LLM.

        Args:
            messages: The list of messages about to be sent to the LLM.

        Returns:
            The (possibly transformed) message list.
        """
        return messages


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


class SummarizationMiddleware(Middleware):
    """Compress older conversation messages when approaching token limits.

    Before each LLM call, checks the total character count. If it
    exceeds ``max_tokens * 4`` (approx 4 chars per token), older
    messages are summarized by an LLM into a single HumanMessage,
    keeping the most recent ``keep_recent`` messages intact.

    Args:
        llm: LLM instance for generating summaries.
        max_tokens: Approximate token threshold. Default 4000.
        keep_recent: Number of most recent messages to keep
            un-summarized. Default 3.

    Examples:
        >>> agent = Agent(
        ...     llm=llm, tools=[...],
        ...     middleware=[
        ...         SummarizationMiddleware(
        ...             llm=llm, max_tokens=2000, keep_recent=3,
        ...         ),
        ...     ],
        ... )
    """

    def __init__(
        self, llm, max_tokens: int = 4000, keep_recent: int = 3
    ) -> None:
        self._llm = llm
        self.max_tokens = max_tokens
        self.keep_recent = keep_recent

    def before_llm(self, messages: list) -> list:
        total_chars = sum(len(m.content) for m in messages if hasattr(m, "content"))
        if total_chars < self.max_tokens * 4:
            return messages

        if len(messages) <= self.keep_recent:
            return messages

        split = len(messages) - self.keep_recent
        older = messages[:split]
        recent = messages[split:]

        combined = "\n".join(
            f"[{m.role}]: {m.content}" for m in older if hasattr(m, "role")
        )
        summary = self._summarize(combined)

        from langchain.schema import HumanMessage
        return [HumanMessage(content=f"Previous conversation summary:\n{summary}")] + list(recent)

    def _summarize(self, text: str) -> str:
        prompt = (
            "Summarize the following conversation concisely, "
            "preserving key facts, decisions, and important details.\n\n"
            f"Conversation:\n{text}\n\nSummary:"
        )
        return self._llm.generate([prompt])[0]


class ModelCallLimitMiddleware(Middleware):
    """Cap the number of LLM calls per Agent run.

    Each call to ``before_llm`` increments an internal counter. When
    ``max_calls`` is exceeded, returns a single limit message instead
    of the original messages — stopping the Agent from making more
    LLM calls.

    Args:
        max_calls: Maximum number of LLM calls allowed. Default 20.

    Examples:
        >>> agent = Agent(
        ...     llm=llm, tools=[...],
        ...     middleware=[ModelCallLimitMiddleware(max_calls=10)],
        ... )
    """

    def __init__(self, max_calls: int = 20) -> None:
        self.max_calls = max_calls
        self._count = 0

    def reset(self) -> None:
        self._count = 0

    def before_llm(self, messages: list) -> list:
        self._count += 1
        if self._count > self.max_calls:
            from langchain.schema import HumanMessage
            return [HumanMessage(content="Model call limit exceeded.")]
        return messages


class ToolCallLimitMiddleware(Middleware):
    """Cap the number of tool calls, globally or per tool.

    Each call to ``before_tool`` increments counters. Limits can be
    set globally (``max_calls``) or per-tool (``per_tool`` dict).
    When a limit is exceeded, ``before_tool`` returns ``(False, msg)``
    and the tool is skipped.

    Args:
        max_calls: Global limit across all tools. None = no global limit.
        per_tool: Dict mapping tool name to max calls for that tool.
            Tools not listed have no limit (unless max_calls applies).

    Examples:
        >>> agent = Agent(
        ...     llm=llm, tools=[calculator, search],
        ...     middleware=[
        ...         ToolCallLimitMiddleware(
        ...             max_calls=10,
        ...             per_tool={"calculator": 3},
        ...         ),
        ...     ],
        ... )
    """

    def __init__(
        self,
        max_calls: Optional[int] = None,
        per_tool: Optional[Dict[str, int]] = None,
    ) -> None:
        self.max_calls = max_calls
        self.per_tool = per_tool or {}
        self._counts: Dict[str, int] = {}

    def reset(self) -> None:
        self._counts.clear()

    def before_tool(self, tool_name: str, tool_input: str) -> tuple:
        self._counts[tool_name] = self._counts.get(tool_name, 0) + 1

        if tool_name in self.per_tool:
            if self._counts[tool_name] > self.per_tool[tool_name]:
                return (False, f"Tool '{tool_name}' call limit exceeded.")

        if self.max_calls is not None:
            total = sum(self._counts.values())
            if total > self.max_calls:
                return (False, "Global tool call limit exceeded.")

        return (True, tool_input)
