"""LLMChain - compose a PromptTemplate with an LLM into an executable chain.

The fundamental primitive of LangChain v0.0.1: ``prompt + llm = chain``.
LLMChain takes input variables, formats them through a PromptTemplate,
sends the resulting prompt to an LLM, and returns the LLM's response.
"""

from typing import Dict, List

from langchain.llms.base import LLM
from langchain.prompts.prompt import PromptTemplate


class LLMChain:
    """Chain that composes a PromptTemplate with an LLM.

    LLMChain is the simplest and most fundamental chain: it takes a
    PromptTemplate and an LLM, and provides ``run`` (single input)
    and ``apply`` (batch input) methods for executing the chain.

    Args:
        prompt: A PromptTemplate that formats input variables into
            a prompt string.
        llm: An LLM instance that generates responses from prompts.

    Examples:
        >>> from langchain.prompts import PromptTemplate
        >>> from langchain.llms import FakeLLM
        >>> from langchain.chains import LLMChain
        >>> prompt = PromptTemplate("What is {topic}?")
        >>> llm = FakeLLM(responses={"What is Python?": "A programming language"})
        >>> chain = LLMChain(prompt=prompt, llm=llm)
        >>> chain.run(topic="Python")
        'A programming language'
    """

    def __init__(self, prompt: PromptTemplate, llm: LLM) -> None:
        self.prompt = prompt
        self.llm = llm

    def run(self, **kwargs: str) -> str:
        """Execute the chain with a single input and return one response.

        Format the PromptTemplate with the provided keyword arguments,
        send the resulting prompt to the LLM, and return the single
        response string.

        Args:
            **kwargs: Input variables matching the PromptTemplate's
                ``input_variables``.

        Returns:
            A single response string from the LLM.
        """
        formatted = self.prompt.format(**kwargs)
        responses = self.llm.generate([formatted])
        return responses[0]

    def apply(self, input_list: List[Dict[str, str]]) -> List[str]:
        """Execute the chain with multiple inputs and return a list of responses.

        For each if'dnput dictionary in ``input_list``, format the
        PromptTemplate, send the prompt to the LLM, and collect the
        responses.

        Args:
            input_list: A list of dictionaries, each containing values
                for the PromptTemplate's ``input_variables``.

        Returns:
            A list of response strings, one for each input dictionary.
        """
        prompts = [self.prompt.format(**inputs) for inputs in input_list]
        return self.llm.generate(prompts)