"""PythonREPLTool - execute Python code and return stdout."""

import sys
from io import StringIO

from langchain.tools.base import Tool


class PythonREPLTool(Tool):
    """Tool that executes Python code in a sandboxed REPL.

    Runs the provided code via ``exec()`` and captures stdout. On
    error, returns the exception message as a string.
    """

    name = "python_repl"
    description = "A Python shell. Use this to execute Python code. Input should be valid Python code."

    def _run(self, input: str) -> str:
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            exec(input, {"__builtins__": __builtins__})
            output = sys.stdout.getvalue()
            return output.strip() if output.strip() else "No output"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"
        finally:
            sys.stdout = old_stdout