"""LLMChain - compose a PromptTemplate with an LLM into an executable chain.

The fundamental primitive of LangChain: ``prompt + llm = chain``.
LLMChain takes input variables, formats them through a PromptTemplate,
sends the resulting prompt to an LLM, optionally parses the output,
and returns the result.
"""

from typing import Any, Dict, Generator, List, Optional

from langchain.callbacks.base import CallbackHandler
from langchain.llms.base import LLM
from langchain.memory.base import Memory
from langchain.output_parsers.base import OutputParser
from langchain.prompts.prompt import PromptTemplate


class LLMChain:
    """Chain that composes a PromptTemplate with an LLM and optional OutputParser.

    LLMChain takes a PromptTemplate and an LLM, and optionally an
    OutputParser. When a parser is provided, ``run`` and ``apply``
    return parsed data (dict, list, etc.) instead of raw strings.
    Without a parser, behavior is identical to v0.0.1.

    Args:
        prompt: A PromptTemplate that formats input variables into
            a prompt string.
        llm: An LLM instance that generates responses from prompts.
        output_parser: Optional OutputParser to parse LLM responses.

    Examples:
        Without parser (v0.0.1 behavior)::

            >>> chain = LLMChain(prompt=prompt, llm=llm)
            >>> chain.run(topic="Python")
            'Python is a programming language'

        With JsonOutputParser::

            >>> from langchain.output_parsers import JsonOutputParser
            >>> chain = LLMChain(prompt=prompt, llm=llm,
            ...                   output_parser=JsonOutputParser())
            >>> chain.run(topic="Python")
            {'topic': 'Python', 'description': 'A programming language'}
    """

    @property
    def output_keys(self) -> List[str]:
        """Keys this chain produces in dict-format output.

        When no ``output_parser`` is set, defaults to ``["text"]``.
        When a parser is configured that returns a dict, reflects the
        dict's expected keys.
        """
        if self.output_parser is not None:
            # JsonOutputParser and similar parsers that return dicts
            # expose their expected keys via output_keys attribute
            if hasattr(self.output_parser, "output_keys"):
                return self.output_parser.output_keys
        return ["text"]

    def __init__(
        self,
        prompt: PromptTemplate,
        llm: LLM,
        output_parser: Optional[OutputParser] = None,
        memory: Optional[Memory] = None,
        callbacks: Optional[List[CallbackHandler]] = None,
    ) -> None:
        self.prompt = prompt
        self.llm = llm
        self.output_parser = output_parser
        self.memory = memory
        self.callbacks = callbacks or []

    def _fire(self, event: str, **kwargs) -> None:
        """Invoke an event on all registered callback handlers."""
        for handler in self.callbacks:
            getattr(handler, event)(**kwargs)

    def run(self, **kwargs: str) -> Any:
        """Execute the chain with a single input and return one result.

        If ``memory`` is set, conversation history is prepended to the
        prompt and the interaction is saved after execution.

        Args:
            **kwargs: Input variables matching the PromptTemplate's
                ``input_variables``.

        Returns:
            A parsed result (if output_parser is set) or a raw response
            string (if not).
        """
        try:
            self._fire("on_chain_start", inputs=kwargs)
            history = self.memory.load_context() if self.memory else ""
            if history:
                formatted = history + "\n" + self.prompt.format(**kwargs)
            else:
                formatted = self.prompt.format(**kwargs)
            self._fire("on_llm_start", prompt=formatted)
            responses = self.llm.generate([formatted])
            result = responses[0]
            self._fire("on_llm_end", response=result)

            if self.memory:
                output_dict = {"text": result}
                if self.output_parser:
                    parsed = self.output_parser.parse(result)
                    if isinstance(parsed, dict):
                        output_dict = parsed
                    else:
                        output_dict = {self.output_keys[0]: parsed}
                self.memory.save_context(kwargs, output_dict)

            if self.output_parser:
                output = self.output_parser.parse(result)
            else:
                output = result
            self._fire("on_chain_end", output=output)
            return output
        except Exception as e:
            self._fire("on_error", error=e)
            raise

    def stream(self, **kwargs: str) -> Generator[str, None, None]:
        """Execute the chain in streaming mode, yielding tokens.

        Behaves like ``run()`` for prompt construction and memory
        loading, but uses the LLM's ``stream()`` method instead of
        ``generate()``. Each token from the LLM is yielded and
        ``on_llm_new_token`` is fired on callbacks.

        Memory is saved after streaming completes — the full
        concatenated response is stored, not individual tokens.

        Args:
            **kwargs: Input variables matching the PromptTemplate's
                ``input_variables``.

        Yields:
            Token strings one at a time from the LLM.
        """
        self._fire("on_chain_start", inputs=kwargs)
        history = self.memory.load_context() if self.memory else ""
        if history:
            formatted = history + "\n" + self.prompt.format(**kwargs)
        else:
            formatted = self.prompt.format(**kwargs)
        self._fire("on_llm_start", prompt=formatted)

        tokens = []
        for token in self.llm.stream(formatted):
            self._fire("on_llm_new_token", token=token)
            tokens.append(token)
            yield token

        full_response = "".join(tokens)
        self._fire("on_llm_end", response=full_response)

        if self.memory:
            self.memory.save_context(kwargs, {"text": full_response})

        self._fire("on_chain_end", output=full_response)

    def _call_internal(self, **kwargs: str) -> Dict[str, Any]:
        """Execute the chain and return output as a dict.

        Unlike ``run()`` which returns a bare value for convenience,
        ``_call_internal()`` always returns a dict keyed by
        ``output_keys``. This enables SequentialChain to merge outputs
        into subsequent chain inputs.

        Args:
            **kwargs: Input variables matching the PromptTemplate's
                ``input_variables``.

        Returns:
            A dict with keys from ``output_keys`` and values from
            the LLM response (parsed or raw).
        """
        formatted = self.prompt.format(**kwargs)
        responses = self.llm.generate([formatted])
        result = responses[0]
        if self.output_parser:
            parsed = self.output_parser.parse(result)
            if isinstance(parsed, dict):
                return parsed
            # Parser returned a non-dict value; wrap it under the
            # default output key
            return {self.output_keys[0]: parsed}
        return {"text": result}

    def apply(self, input_list: List[Dict[str, str]]) -> List[Any]:
        """Execute the chain with multiple inputs and return a list of results.

        If ``output_parser`` is set, each LLM response is parsed before
        returning. Otherwise returns raw response strings.

        Args:
            input_list: A list of dictionaries, each containing values
                for the PromptTemplate's ``input_variables``.

        Returns:
            A list of parsed results or raw response strings.
        """
        prompts = [self.prompt.format(**inputs) for inputs in input_list]
        responses = self.llm.generate(prompts)
        if self.output_parser:
            return [self.output_parser.parse(r) for r in responses]
        return responses