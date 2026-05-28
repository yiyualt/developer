"""StdOutCallbackHandler - prints execution events to stdout.

The simplest way to observe what's happening inside your chains
and agents. Just attach it and watch the events flow:

    handler = StdOutCallbackHandler()
    chain = LLMChain(llm=OpenAI(), callbacks=[handler])
    chain.run(question="What is Python?")

    # stdout:
    # [LLMChain] Start: What is Python?
    # [LLM] Start: Answer this question concisely: What is Python?
    # [LLM] End: Python is a programming language
    # [LLMChain] End: Python is a programming language
"""

from langchain.callbacks.base import CallbackHandler


class StdOutCallbackHandler(CallbackHandler):
    """CallbackHandler that prints execution events to stdout.

    Each event is formatted as [ComponentType] Event: detail,
    making it easy to follow the execution flow in a terminal.
    """

    def on_llm_start(self, **kwargs) -> None:
        prompt = kwargs.get("prompt", "")
        print(f"[LLM] Start: {prompt}")

    def on_llm_end(self, **kwargs) -> None:
        response = kwargs.get("response", "")
        print(f"[LLM] End: {response}")

    def on_chain_start(self, **kwargs) -> None:
        inputs = kwargs.get("inputs", {})
        print(f"[LLMChain] Start: {inputs}")

    def on_chain_end(self, **kwargs) -> None:
        output = kwargs.get("output", "")
        print(f"[LLMChain] End: {output}")

    def on_tool_start(self, **kwargs) -> None:
        tool_name = kwargs.get("tool_name", "")
        tool_input = kwargs.get("tool_input", "")
        print(f"[Tool] Start: {tool_name}({tool_input})")

    def on_tool_end(self, **kwargs) -> None:
        output = kwargs.get("output", "")
        print(f"[Tool] End: {output}")

    def on_agent_action(self, **kwargs) -> None:
        action = kwargs.get("action", "")
        print(f"[Agent] Action: {action}")

    def on_agent_finish(self, **kwargs) -> None:
        final_answer = kwargs.get("final_answer", "")
        print(f"[Agent] Finish: {final_answer}")

    def on_error(self, **kwargs) -> None:
        error = kwargs.get("error", "")
        print(f"[Error] {error}")