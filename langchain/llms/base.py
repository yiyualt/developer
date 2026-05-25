"""LLM base class - the abstract interface for all language model calls.

LangChain v0.0.1 defines a single unified interface for LLM interaction:
``LLM`` is an ABC that requires subclasses to implement ``_generate``.
The public ``generate`` method handles the contract between caller and model.
"""

from abc import ABC, abstractmethod
from typing import List


class LLM(ABC):
    """Abstract base class for large language model implementations.

    All LLM subclasses MUST implement the ``_generate`` method, which
    accepts a list of prompt strings and returns a list of response strings.

    The public ``generate`` method delegates to ``_generate`` and serves
    as the standard entry point for LLM calls within a chain.

    Examples:
        Subclass implementation::

            class MyLLM(LLM):
                def _generate(self, prompts: list[str]) -> list[str]:
                    return ["response" for _ in prompts]
    """

    @abstractmethod
    def _generate(self, prompts: List[str]) -> List[str]:
        """Generate responses for a list of prompts.

        This is the core method that each LLM subclass MUST implement.
        It receives a list of prompt strings and returns a corresponding
        list of response strings, one per prompt.

        Args:
            prompts: A list of prompt strings to send to the model.

        Returns:
            A list of response strings, one for each input prompt.
        """

    def generate(self, prompts: List[str]) -> List[str]:
        """Generate responses for a list of prompts.

        This is the public entry point for LLM calls. It delegates to
        the subclass's ``_generate`` implementation.

        Args:
            prompts: A list of prompt strings to send to the model.

        Returns:
            A list of response strings, one for each input prompt.
        """
        return self._generate(prompts)