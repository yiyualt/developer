"""RouterChain - dynamically select which Chain to execute based on input.

RouterChain introduces conditional branching to LangChain. Instead of
always executing a fixed pipeline, the Router examines the user's
question and chooses the most appropriate Chain to run.

This is the "Dynamic Option Injection" pattern — the same pattern
Agent uses for selecting Tools, applied at the Chain level:

- Agent:  dynamically selects a Tool  (micro-level)
- Router: dynamically selects a Chain (macro-level)

LLMRouterChain uses an LLM + JsonOutputParser to make routing
decisions. The prompt is auto-generated from the destinations'
names and descriptions, so no manual prompt writing is needed.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from langchain.chains.llm_chain import LLMChain
from langchain.llms.base import LLM
from langchain.output_parsers.json import JsonOutputParser
from langchain.prompts.prompt import PromptTemplate


ROUTER_PROMPT_TEMPLATE = """You are a router. Given a question, choose the most appropriate chain to handle it.

Available chains:
{destinations}

Output JSON with the chain name. Example: chain: retrieval

Question: {question}"""


@dataclass
class ChainDestination:
    """A target Chain that the Router can select.

    Attributes:
        name: Unique identifier for this destination (used in routing output).
        description: Short text describing when this chain should be selected.
            This is what the LLM reads to make its routing decision.
        chain: The Chain instance to execute when this destination is selected.
            Can be any Chain type — LLMChain, RetrievalChain, Agent, etc.
    """

    name: str
    description: str
    chain: Any


class RouterChain(ABC):
    """Abstract base class for chain routing.

    Every RouterChain must implement route() to select a destination
    and run() to execute the selected chain.
    """

    @abstractmethod
    def route(self, question: str) -> str:
        """Select a destination chain name based on the question.

        Args:
            question: The user's question to route.

        Returns:
            The name of the selected ChainDestination.
        """
        ...

    @abstractmethod
    def run(self, question: str) -> Any:
        """Route the question and execute the selected chain.

        Args:
            question: The user's question.

        Returns:
            The result of the selected chain's run() method.
        """
        ...


class LLMRouterChain(RouterChain):
    """Router that uses an LLM to select which Chain to execute.

    The LLM receives a prompt listing all available destinations
    (name + description) and outputs JSON {"chain": "<name>"}.
    JsonOutputParser extracts the chain name, and the corresponding
    ChainDestination's chain is executed.

    If the LLM output cannot be parsed or doesn't match any
    destination name, the default_destination is used as fallback.

    Args:
        llm: An LLM instance for making routing decisions.
        destinations: A list of ChainDestination objects.
        default_destination: A ChainDestination to use as fallback
            when routing fails. Must not be None.

    Examples:
        Multi-prompt routing::

            >>> from langchain import LLMRouterChain, ChainDestination, LLMChain, OpenAI
            >>> general_chain = LLMChain(prompt=general_prompt, llm=OpenAI())
            >>> retrieval_chain = RetrievalChain(...)
            >>> router = LLMRouterChain(
            ...     llm=OpenAI(),
            ...     destinations=[
            ...         ChainDestination("general", "General knowledge", general_chain),
            ...         ChainDestination("retrieval", "Document questions", retrieval_chain),
            ...     ],
            ...     default_destination=ChainDestination("general", "...", general_chain),
            ... )
            >>> router.run(question="What is the refund policy?")
    """

    def __init__(
        self,
        llm: LLM,
        destinations: list[ChainDestination],
        default_destination: ChainDestination,
    ) -> None:
        self.llm = llm
        self.destinations = destinations
        self.default_destination = default_destination
        self._dest_map = {d.name: d for d in destinations}
        self._dest_map[default_destination.name] = default_destination

        # Router chain: LLM + JsonOutputParser
        self._parser = JsonOutputParser(strict=False)
        self._router_chain = LLMChain(
            prompt=self._build_prompt(),
            llm=self.llm,
            output_parser=self._parser,
        )

    def _build_prompt(self) -> PromptTemplate:
        """Auto-generate the routing prompt from destinations.

        Pre-fills the destinations text into the template so the
        resulting PromptTemplate only has {question} as an
        input_variable.
        """
        dest_lines = [
            f"- {d.name}: {d.description}"
            for d in self.destinations
        ]
        if self.default_destination.name not in {d.name for d in self.destinations}:
            dest_lines.append(
                f"- {self.default_destination.name}: {self.default_destination.description}"
            )
        destinations_text = "\n".join(dest_lines)

        # Replace {destinations} in template, leaving {question} intact
        filled_template = ROUTER_PROMPT_TEMPLATE.replace("{destinations}", destinations_text)

        return PromptTemplate(template=filled_template)

    def route(self, question: str) -> str:
        """Use the LLM to select a destination chain name.

        Args:
            question: The user's question to route.

        Returns:
            The name of the selected destination, or the
            default_destination name if routing fails.
        """
        result = self._router_chain.run(question=question)

        if isinstance(result, dict) and "chain" in result:
            chain_name = result["chain"]
            if chain_name in self._dest_map:
                return chain_name

        return self.default_destination.name

    def run(self, question: str) -> Any:
        """Route the question and execute the selected chain.

        Args:
            question: The user's question.

        Returns:
            The result of the selected chain's run() method.
        """
        dest_name = self.route(question)
        destination = self._dest_map[dest_name]
        return destination.chain.run(question=question)