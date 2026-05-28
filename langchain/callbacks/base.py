"""CallbackHandler - lifecycle hooks for observing component execution.

Every component (LLMChain, Agent, Tool) runs as a black box —
no way to see what's happening inside. CallbackHandler opens a
window: components invoke hooks at key execution points, and
handlers receive those events for logging, debugging, or tracing.

The hooks are:
- on_llm_start / on_llm_end — before and after LLM calls
- on_chain_start / on_chain_end — before and after Chain execution
- on_tool_start / on_tool_end — before and after Tool execution
- on_agent_action / on_agent_finish — Agent reasoning steps
- on_error — when any step raises an exception

Each hook accepts **kwargs for extensibility — event payloads
vary by component type, and future hooks may add new fields
without breaking existing handler implementations.
"""

from abc import ABC


class CallbackHandler(ABC):
    """Abstract base class for execution lifecycle hooks.

    Subclass this to receive events from LLMChain, Agent, Tool,
    and other components. All hook methods are no-ops by default
    — override only the ones you need.

    Components call these hooks at key execution points:
        on_chain_start → on_llm_start → on_llm_end → on_chain_end
        on_agent_action → on_tool_start → on_tool_end → on_agent_finish
        on_error (if any step raises an exception)

    Args are passed as **kwargs so handlers can ignore fields
    they don't need, and future extensions won't break old handlers.
    """

    def on_llm_start(self, **kwargs) -> None:
        """Called before an LLM invocation.

        kwargs typically include:
            prompt (str): The formatted prompt sent to the LLM.
        """

    def on_llm_end(self, **kwargs) -> None:
        """Called after an LLM invocation completes.

        kwargs typically include:
            response (str): The LLM's response text.
        """

    def on_chain_start(self, **kwargs) -> None:
        """Called before a Chain starts execution.

        kwargs typically include:
            inputs (dict): The input variables for the chain.
        """

    def on_chain_end(self, **kwargs) -> None:
        """Called after a Chain completes execution.

        kwargs typically include:
            output (str): The chain's output.
        """

    def on_tool_start(self, **kwargs) -> None:
        """Called before a Tool execution.

        kwargs typically include:
            tool_name (str): The tool's name.
            tool_input (str): The input passed to the tool.
        """

    def on_tool_end(self, **kwargs) -> None:
        """Called after a Tool execution completes.

        kwargs typically include:
            output (str): The tool's output.
        """

    def on_agent_action(self, **kwargs) -> None:
        """Called when an Agent decides on a tool action.

        kwargs typically include:
            action (str): The action string, e.g. "calculator[2+3]".
        """

    def on_agent_finish(self, **kwargs) -> None:
        """Called when an Agent produces a Final Answer.

        kwargs typically include:
            final_answer (str): The agent's final answer.
        """

    def on_error(self, **kwargs) -> None:
        """Called when any execution step raises an exception.

        kwargs typically include:
            error (Exception): The exception that was raised.
        """