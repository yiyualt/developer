"""LLM base class - the abstract interface for all language model calls.

LangChain v0.0.1 defines a single unified interface for LLM interaction:
``LLM`` is an ABC that requires subclasses to implement ``_generate``.
The public ``generate`` method handles the contract between caller and model.
"""

from abc import abstractmethod
from typing import Any, Generator, List

from langchain.runnables import Runnable


class LLM(Runnable):
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

    def invoke(self, input: Any, **kwargs: Any) -> Any:
        """Runnable interface — generate a response from a prompt string.

        Args:
            input: A prompt string.

        Returns:
            The LLM's response string.
        """
        return self.generate([input])[0]

    def _stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream tokens for a single prompt.

        Subclasses MAY implement this for token-by-token generation.
        If not implemented, calling ``stream()`` raises NotImplementedError.

        Args:
            prompt: A single prompt string.

        Yields:
            Token strings one at a time.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support streaming. "
            "Implement _stream() to enable token-by-token generation."
        )

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream tokens for a single prompt.

        This is the public entry point for streaming LLM calls.
        It delegates to the subclass's ``_stream`` implementation.
        Each yielded token is a string; concatenating all tokens
        equals the full response.

        Args:
            prompt: A single prompt string.

        Yields:
            Token strings one at a time.
        """
        return self._stream(prompt)

    async def _agenerate(self, prompts: List[str]) -> List[str]:
        """Async concurrent generation for a list of prompts.

        Subclasses MAY implement this for concurrent LLM calls.
        If not implemented, ``agenerate()`` falls back to calling
        ``generate()`` synchronously.

        Args:
            prompts: A list of prompt strings to send to the model.

        Returns:
            A list of response strings, one for each input prompt.
        """
        return self._generate(prompts)

    async def agenerate(self, prompts: List[str]) -> List[str]:
        """Async concurrent generation for a list of prompts.

        This is the public entry point for async LLM calls. If the
        subclass implements ``_agenerate``, prompts are processed
        concurrently. Otherwise, falls back to synchronous ``generate``.

        Args:
            prompts: A list of prompt strings to send to the model.

        Returns:
            A list of response strings, one for each input prompt,
            in the same order as the input prompts.
        """
        return await self._agenerate(prompts)