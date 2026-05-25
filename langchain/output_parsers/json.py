"""JsonOutputParser - extract and parse JSON from LLM output text.

LLMs often return JSON embedded in markdown code blocks or surrounded
by extra text. JsonOutputParser handles both cases by first extracting
the JSON portion, then parsing it with json.loads.
"""

import json
import re
from typing import Any, Dict

from langchain.output_parsers.base import OutputParser


class JsonOutputParser(OutputParser):
    """Parse LLM output into a Python dict by extracting JSON from text.

    Handles three common LLM output patterns:
    1. Raw JSON: ``{"key": "value"}``
    2. JSON in markdown code block: `````json {"key": "value"} `````
    3. JSON mixed with explanatory text

    Args:
        strict: If True, raise ValueError on any parsing failure.
            If False, return empty dict on failure. Defaults to True.

    Examples:
        >>> from langchain.output_parsers import JsonOutputParser
        >>> parser = JsonOutputParser()
        >>> parser.parse('{"topic": "Python"}')
        {'topic': 'Python'}

        >>> parser.parse('Result:\\n```json\\n{"topic": "Python"}\\n```')
        {'topic': 'Python'}
    """

    def __init__(self, strict: bool = True) -> None:
        self.strict = strict

    def parse(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM output text.

        First attempts to find JSON inside a markdown code block
        (`````json ... `````). If none found, searches for a raw JSON
        object pattern. The extracted string is then parsed with
        ``json.loads``.

        Args:
            text: Raw LLM response text containing JSON.

        Returns:
            A Python dict parsed from the JSON.

        Raises:
            ValueError: If no JSON is found or JSON parsing fails
                (only when ``strict=True``).
        """
        # Try markdown code block first
        code_block_match = re.search(
            r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL
        )
        if code_block_match:
            json_str = code_block_match.group(1).strip()
            return self._load_json(json_str)

        # Try raw JSON object
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return self._load_json(json_str)

        if self.strict:
            raise ValueError(f"No JSON found in text: {text[:200]}...")
        return {}

    def _load_json(self, json_str: str) -> Dict[str, Any]:
        """Parse a JSON string, raising ValueError on failure if strict."""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            if self.strict:
                raise ValueError(f"JSON parsing failed: {e}")
            return {}