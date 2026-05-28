"""OpenAI-compatible LLM - calls any OpenAI Chat Completions compatible API.

Supports OpenAI, DashScope, and any provider that offers an
OpenAI-compatible endpoint. Configuration via constructor parameters,
environment variables, or ``.env`` file.
"""

import asyncio
import os
from pathlib import Path
from typing import Generator, List, Optional

import openai
from dotenv import load_dotenv

from langchain.llms.base import LLM

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class OpenAI(LLM):
    """OpenAI-compatible Chat Completions LLM implementation.

    Works with any provider that exposes an OpenAI-compatible Chat
    Completions API. Sends each prompt as a single ``user`` message
    and returns the first choice's ``content``.

    Configuration is resolved in this order:
    1. Constructor parameters (highest priority)
    2. ``.env`` file in the project root
    3. Environment variables

    Args:
        model_name: Model to use. Defaults to ``LLM_MODEL`` env var or ``gpt-4o-mini``.
        temperature: Sampling temperature (0 = deterministic). Defaults to 0.7.
        max_tokens: Maximum tokens in the response. Defaults to None.
        openai_api_key: API key. Defaults to ``LLM_API_KEY`` or ``OPENAI_API_KEY`` env var.
        base_url: API endpoint URL. Defaults to ``LLM_BASE_URL`` or ``OPENAI_BASE_URL`` env var.

    Raises:
        ValueError: If no API key is available.

    Examples:
        >>> from langchain.llms import OpenAI
        >>> llm = OpenAI()  # reads from .env
        >>> llm.generate(["What is Python?"])
        ['Python is a high-level programming language...']

        Explicit configuration::

            llm = OpenAI(
                model_name="glm-5.1",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                openai_api_key="sk-xxx",
            )
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        openai_api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.model_name = model_name or os.environ.get("LLM_MODEL") or "gpt-4o-mini"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.openai_api_key = (
            openai_api_key
            or os.environ.get("LLM_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        self.base_url = (
            base_url
            or os.environ.get("LLM_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
        )
        if not self.openai_api_key:
            raise ValueError(
                "API key not found. Set LLM_API_KEY in .env file, "
                "environment variable, or pass openai_api_key parameter."
            )
        self._client = openai.OpenAI(
            api_key=self.openai_api_key,
            base_url=self.base_url,
        )
        self._async_client = openai.AsyncOpenAI(
            api_key=self.openai_api_key,
            base_url=self.base_url,
        )

    def _generate(self, prompts: List[str]) -> List[str]:
        """Generate responses by calling Chat Completions API.

        Each prompt string is sent as a single ``user`` message. The
        ``content`` of the first choice in each response is returned.

        Args:
            prompts: A list of prompt strings.

        Returns:
            A list of response strings, one for each prompt.
        """
        responses = []
        for prompt in prompts:
            completion = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            responses.append(completion.choices[0].message.content)
        return responses

    def _stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream tokens for a single prompt via Chat Completions API.

        Uses ``stream=True`` to get token-by-token responses from the
        API. Each chunk's ``content`` delta is yielded as a token.

        Args:
            prompt: A single prompt string.

        Yields:
            Token strings one at a time.
        """
        stream = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content is not None:
                yield delta.content

    async def _agenerate(self, prompts: List[str]) -> List[str]:
        """Concurrently generate responses via AsyncOpenAI client.

        Uses ``asyncio.gather`` to call all prompts concurrently via
        the AsyncOpenAI client. Results are returned in input order.

        Args:
            prompts: A list of prompt strings.

        Returns:
            A list of response strings, in the same order as input.
        """
        async def _call_one(prompt: str) -> str:
            completion = await self._async_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return completion.choices[0].message.content

        return await asyncio.gather(*[_call_one(p) for p in prompts])