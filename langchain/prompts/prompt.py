"""PromptTemplate - format variables into template strings to produce prompts.

The core primitive of LangChain v0.0.1: a template with ``{variable}``
placeholders that are filled in with provided values to generate a
complete prompt string for an LLM.
"""

import re
from string import Formatter
from typing import List


class PromptTemplate:
    """A template string with ``{variable}`` placeholders for prompt generation.

    PromptTemplate extracts variable names from a template string and
    validates that provided inputs match the expected variables on format.

    Args:
        template: A string containing ``{variable_name}`` placeholders.
        input_variables: Optional explicit list of variable names. If not
            provided, variables are automatically extracted from the template.

    Examples:
        >>> from langchain.prompts import PromptTemplate
        >>> template = PromptTemplate("Tell me about {topic}")
        >>> template.format(topic="Python")
        'Tell me about Python'
        >>> template.input_variables
        ['topic']
    """

    def __init__(self, template: str, input_variables: List[str] | None = None) -> None:
        self.template = template
        self.input_variables = input_variables or self._extract_variables(template)

    @staticmethod
    def _extract_variables(template: str) -> List[str]:
        """Extract ``{variable}`` names from a template string.

        Uses Python's string.Formatter to parse the template and collect
        all field names.

        Args:
            template: The template string to parse.

        Returns:
            A sorted list of unique variable names found in the template.
        """
        formatter = Formatter()
        variables = []
        for _, field_name, _, _ in formatter.parse(template):
            if field_name is not None:
                variables.append(field_name)
        return sorted(set(variables))

    def format(self, **kwargs: str) -> str:
        """Format the template by substituting variables with provided values.

        All variables declared in ``input_variables`` MUST be provided as
        keyword arguments. Extra keyword arguments that are not in
        ``input_variables`` are rejected.

        Args:
            **kwargs: Values for each input variable.

        Returns:
            The formatted prompt string with all placeholders filled in.

        Raises:
            KeyError: If a required input variable is missing.
            ValueError: If an unexpected keyword argument is provided.

        Examples:
            >>> template = PromptTemplate("Hello {name}!")
            >>> template.format(name="World")
            'Hello World!'
        """
        missing = set(self.input_variables) - set(kwargs.keys())
        if missing:
            raise KeyError(
                f"Missing required input variables: {sorted(missing)}"
            )

        extra = set(kwargs.keys()) - set(self.input_variables)
        if extra:
            raise ValueError(
                f"Unexpected input variables: {sorted(extra)}. "
                f"Expected: {self.input_variables}"
            )

        return self.template.format(**kwargs)