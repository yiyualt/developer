"""SearchTool - simulated web search with mock results."""

from langchain.tools.base import Tool


class SearchTool(Tool):
    """Tool that simulates a web search with pre-defined mock results.

    Returns mock results for a set of known queries. For unknown
    queries, returns a generic "no results" response. This tool is
    for demonstration purposes — it does not perform real searches.
    """

    name = "search"
    description = "Useful for searching the web for information. Input should be a search query."

    _mock_results = {
        "python": "Python is a high-level, general-purpose programming language created by Guido van Rossum.",
        "langchain": "LangChain is a framework for developing applications powered by large language models.",
        "react": "ReAct (Reasoning + Acting) is a paradigm where LLMs interleave thinking and tool use.",
    }

    def run(self, input: str) -> str:
        query_lower = input.lower()
        for key, result in self._mock_results.items():
            if key in query_lower:
                return result
        return f"No specific results found for '{input}'"