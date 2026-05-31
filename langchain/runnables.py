"""Runnable — the universal interface for composable components.

LCEL (LangChain Expression Language) unifies all components under a
single interface: ``Runnable.invoke(input) -> output``. Components
are composed with the ``|`` operator — ``prompt | llm | parser`` —
instead of manually constructing intermediate chain objects.

This is the foundation that every LangChain component eventually
implements. From PromptTemplate to Agent, everything becomes a
Runnable.
"""

from abc import ABC, abstractmethod
from typing import Any


class Runnable(ABC):
    """Abstract base class for composable components.

    Every Runnable implements ``invoke(input) -> output`` and can
    be chained with ``|`` to form a ``RunnableSequence``.

    Subclasses must implement ``invoke``.
    """

    @abstractmethod
    def invoke(self, input: Any, **kwargs: Any) -> Any:
        """Transform an input into an output.

        Args:
            input: The input data.
            **kwargs: Additional keyword arguments.

        Returns:
            The transformed output.
        """
        ...

    def __or__(self, other: "Runnable") -> "RunnableSequence":
        """Pipe this Runnable into another.

        ``a | b`` returns a RunnableSequence that runs ``a`` first,
        then passes its output as input to ``b``.

        Args:
            other: The next Runnable in the pipeline.

        Returns:
            A RunnableSequence executing ``self`` then ``other``.
        """
        return RunnableSequence(self, other)


class RunnableSequence(Runnable):
    """A sequence of Runnable steps executed in order.

    RunnableSequence is created by the ``|`` operator. Each step's
    output becomes the next step's input, left to right.

    Args:
        *steps: Runnable instances to execute in order.
    """

    def __init__(self, *steps: Runnable) -> None:
        self.steps = steps

    def invoke(self, input: Any, **kwargs: Any) -> Any:
        """Execute all steps in order, piping output to input.

        Args:
            input: The initial input for the first step.
            **kwargs: Additional keyword arguments.

        Returns:
            The output of the last step.
        """
        result = input
        for step in self.steps:
            result = step.invoke(result, **kwargs)
        return result
