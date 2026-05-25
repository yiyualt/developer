"""LLMChain - compose a PromptTemplate with an LLM into an executable chain.

The fundamental primitive of LangChain: ``prompt + llm = chain``.
LLMChain takes input variables, formats them through a PromptTemplate,
sends the resulting prompt to an LLM, optionally parses the output,
and returns the result.
"""

from typing import Any, Dict, List, Optional

from langchain.llms.base import LLM
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

    def __init__(
        self,
        prompt: PromptTemplate,
        llm: LLM,
        output_parser: Optional[OutputParser] = None,
    ) -> None:
        self.prompt = prompt
        self.llm = llm
        self.output_parser = output_parser

    def run(self, **kwargs: str) -> Any:
        """Execute the chain with a single input and return one result.

        If ``output_parser`` is set, the LLM response is parsed before
        returning. Otherwise returns the raw response string.

        Args:
            **kwargs: Input variables matching the PromptTemplate's
                ``input_variables``.

        Returns:
            A parsed result (if output_parser is set) or a raw response
            string (if not).
        """
        formatted = self.prompt.format(**kwargs)
        responses = self.llm.generate([formatted])
        result = responses[0]
        if self.output_parser:
            return self.output_parser.parse(result)
        return result

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