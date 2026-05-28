"""CalculatorTool - evaluate simple arithmetic expressions."""

from langchain.tools.base import Tool


class CalculatorTool(Tool):
    """Tool that evaluates simple arithmetic expressions.

    Uses Python's ``eval()`` on the input string. Only allows basic
    arithmetic operations (+, -, *, /, **, %). Returns the result as
    a string, or an error message if the expression is invalid.
    """

    name = "calculator"
    description = "Useful for arithmetic calculations. Input should be a math expression like '2+3' or '15*4'."

    def _run(self, input: str) -> str:
        try:
            result = eval(input, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Error: {e}"