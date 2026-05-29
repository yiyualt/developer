"""@tool decorator — convert any function into a Tool with zero boilerplate.

The @tool decorator eliminates the 8-10 lines of class boilerplate
required by Tool subclasses. A decorated function's name becomes the
Tool's ``name``, its docstring becomes ``description``, and the
function body becomes ``_run``.

Usage::

    @tool
    def calculator(input: str) -> str:
        \"\"\"Performs arithmetic calculations.\"\"\"
        return str(eval(input))

    # calculator is now a Tool instance ready for use with Agent
    agent = Agent(llm=llm, tools=[calculator])

With explicit overrides::

    @tool(name="calc", description="Solves math problems")
    def calculator(input: str) -> str:
        return str(eval(input))
"""

import inspect
from typing import Callable, Optional, Union

from langchain.tools.base import Tool


class FunctionTool(Tool):
    """Internal Tool subclass created by the @tool decorator.

    Users should never need to instantiate this directly — use
    ``@tool`` instead.
    """

    def __init__(
        self,
        func: Callable[[str], str],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.name = name or func.__name__
        # Use first non-empty line of docstring as description
        if description:
            self.description = description
        elif func.__doc__:
            first_line = func.__doc__.strip().split("\n")[0].strip()
            self.description = first_line
        else:
            self.description = ""
        self._func = func

    def _run(self, input: str) -> str:
        return self._func(input)


def tool(
    func_or_name=None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Union[Tool, Callable]:
    """Convert a function into a Tool instance.

    Supports two calling conventions:

    1. Direct decoration (no arguments)::

        @tool
        def my_tool(input: str) -> str:
            \"\"\"Does something useful.\"\"\"
            return input

    2. Decoration with arguments::

        @tool(name="custom_name", description="Custom description")
        def my_tool(input: str) -> str:
            return input

    Args:
        func_or_name: Either a callable (mode 1) or a name string (mode 2).
        name: Explicit Tool name (keyword-only, mode 2).
        description: Explicit Tool description (keyword-only, mode 2).

    Returns:
        A Tool instance (mode 1) or a decorator that returns a Tool
        instance (mode 2).
    """
    # Mode 1: @tool — func_or_name is the decorated function
    if callable(func_or_name):
        return FunctionTool(func_or_name)

    # Mode 2: @tool(name=..., description=...) — return a decorator
    def decorator(func):
        return FunctionTool(func, name=name, description=description)

    return decorator
