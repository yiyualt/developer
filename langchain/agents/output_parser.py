"""AgentOutputParser - extract Thought/Action/Final Answer from LLM output."""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentAction:
    """Parsed Action from an LLM response."""

    thought: str
    tool: str
    tool_input: str


@dataclass
class AgentFinish:
    """Parsed Final Answer from an LLM response."""

    thought: str
    final_answer: str


@dataclass
class AgentFallback:
    """Fallback when LLM output has no Action or Final Answer markers."""

    thought: str


def parse_agent_output(text: str) -> AgentAction | AgentFinish | AgentFallback:
    """Parse an LLM response into a structured agent step.

    Supports three formats:
    - ``Thought: ... Action: tool_name[input]`` → AgentAction
    - ``Thought: ... Final Answer: ...`` → AgentFinish
    - Anything else → AgentFallback (treat entire text as a Thought)

    Args:
        text: The raw LLM response string.

    Returns:
        An AgentAction, AgentFinish, or AgentFallback.
    """
    # Extract Thought (up to "Action:" or "Final Answer:" or end of line)
    thought_match = re.search(r"Thought:\s*(.+?)(?:\s*Action:|\s*Final Answer:|\n|$)", text)
    thought = thought_match.group(1).strip() if thought_match else text.strip()

    # Check for Final Answer first (takes priority over Action)
    finish_match = re.search(r"Final Answer:\s*(.*?)$", text, re.DOTALL)
    if finish_match:
        return AgentFinish(thought=thought, final_answer=finish_match.group(1).strip())

    # Check for Action: tool_name[input]
    action_match = re.search(r"Action:\s*(\w+)\[(.*?)\]", text, re.DOTALL)
    if action_match:
        return AgentAction(
            thought=thought,
            tool=action_match.group(1).strip(),
            tool_input=action_match.group(2).strip(),
        )

    # Fallback: no Action or Final Answer found
    return AgentFallback(thought=text.strip())