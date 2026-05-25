"""ListOutputParser - extract comma-separated lists from LLM output text.

LLMs often return lists as comma-separated text, sometimes with extra
explanatory wording. ListOutputParser extracts the list portion and
strips whitespace from each item.
"""

import re
from typing import Any, List

from langchain.output_parsers.base import OutputParser


class ListOutputParser(OutputParser):
    """Parse LLM output into a Python list by extracting comma-separated items.

    Finds the most comma-rich portion of the text and splits it into
    a list of stripped strings. If no commas are found, returns a
    single-item list.

    Examples:
        >>> from langchain.output_parsers import ListOutputParser
        >>> parser = ListOutputParser()
        >>> parser.parse("Python, Rust, Go")
        ['Python', 'Rust', 'Go']

        >>> parser.parse("The languages are: Python, Rust, Go")
        ['Python', 'Rust', 'Go']

        >>> parser.parse("Just one thing")
        ['Just one thing']
    """

    def parse(self, text: str) -> List[str]:
        """Extract comma-separated items from LLM output text.

        Strips surrounding punctuation and whitespace from each item.
        If the text contains no commas, returns a single-item list
        with the stripped text.

        Args:
            text: Raw LLM response text containing a comma-separated list.

        Returns:
            A list of strings.
        """
        # Find the portion with the most commas (most likely the list)
        segments = text.split("\n")
        best_segment = max(segments, key=lambda s: s.count(","))

        # If no commas anywhere, return single item
        if "," not in best_segment:
            return [text.strip()]

        # Split on commas and strip each item
        items = [item.strip() for item in best_segment.split(",")]

        # Remove leading prefix text (e.g., "The languages are:")
        items = [
            re.sub(r"^.*?:\s*", "", items[0]) if i == 0 else item
            for i, item in enumerate(items)
        ]

        # Filter out empty items
        return [item for item in items if item]