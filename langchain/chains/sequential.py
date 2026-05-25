"""SequentialChain - execute multiple LLMChains in sequence.

SequentialChain orchestrates multi-step reasoning by running chains
one after another. Each step's output dict is merged into the next
step's input, enabling key-based data flow across the pipeline.
"""

from typing import Any, Dict, List

from langchain.chains.llm_chain import LLMChain


class SequentialChain:
    """Chain that executes multiple LLMChains in sequence.

    SequentialChain runs a list of LLMChains in order, passing each
    step's output as additional input to the next step. It accumulates
    all outputs and returns a dict containing every key produced by
    every step in the sequence.

    Args:
        chains: A list of LLMChains to execute in order.
        input_variables: A list of key names that must be provided
            in the initial ``run()`` call.

    Examples:
        Two-step sequential chain::

            >>> from langchain.chains import LLMChain, SequentialChain
            >>> step1 = LLMChain(prompt=prompt1, llm=llm,
            ...                   output_parser=JsonOutputParser())
            >>> step2 = LLMChain(prompt=prompt2, llm=llm)
            >>> seq = SequentialChain(
            ...     chains=[step1, step2],
            ...     input_variables=["subject"])
            >>> result = seq.run(subject="Python")
            >>> # result contains all output keys from both steps

    Raises:
        KeyError: If required input variables are missing from ``run()``.
    """

    def __init__(
        self,
        chains: List[LLMChain],
        input_variables: List[str],
    ) -> None:
        self.chains = chains
        self.input_variables = input_variables

    def run(self, **kwargs: str) -> Dict[str, Any]:
        """Execute all chains in sequence and return accumulated output.

        Each chain's output dict is merged into the input for the next
        chain. The final result contains all output keys from every
        step in the sequence.

        Args:
            **kwargs: Values for all declared ``input_variables``.

        Returns:
            A dict containing all output keys from every step.

        Raises:
            KeyError: If any declared ``input_variable`` is not provided.
        """
        # Validate that all required input variables are present
        missing = [v for v in self.input_variables if v not in kwargs]
        if missing:
            raise KeyError(
                f"Missing required input variables: {missing}. "
                f"Expected {self.input_variables}, got {list(kwargs.keys())}"
            )

        accumulated: Dict[str, Any] = dict(kwargs)

        for chain in self.chains:
            # Determine which variables this chain needs
            required = chain.prompt.input_variables
            # Check that all required variables are available in accumulated dict
            unsatisfied = [v for v in required if v not in accumulated]
            if unsatisfied:
                raise KeyError(
                    f"Chain requires input variables {unsatisfied} that are "
                    f"not satisfied by initial inputs or prior step outputs. "
                    f"Available keys: {list(accumulated.keys())}"
                )

            # Build input for this chain from accumulated dict
            chain_input = {v: accumulated[v] for v in required}

            # Execute the chain via _call_internal to get dict output
            step_output = chain._call_internal(**chain_input)

            # Merge step output into accumulated dict
            accumulated.update(step_output)

        return accumulated