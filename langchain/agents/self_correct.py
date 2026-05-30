"""Self-Correction — validate Agent outputs and retry on failure.

Where Agent produces an answer, SelfCorrectingAgent ensures the answer
is correct. It wraps any Agent, validates output with a Corrector,
and retries with feedback if validation fails.

Quality is not a destination — it's a loop.
"""

from typing import Dict, List, Optional

from langchain.agents.agent import Agent
from langchain.callbacks.base import CallbackHandler
from langchain.callbacks.mixin import CallbackMixin
from langchain.llms.base import LLM

CORRECTOR_PROMPT = """You are a quality checker. Evaluate whether the following answer correctly and completely addresses the question.

Question: {question}

Answer to evaluate: {answer}

If the answer is correct, complete, and well-formed, respond with exactly "PASS".
If the answer has any issues, explain what is wrong and how to fix it.

Response:"""


class LLMCorrector(CallbackMixin):
    """Validate answer quality using an LLM evaluator.

    LLMCorrector asks an LLM to judge whether an answer is correct
    and complete. A response starting with "PASS" means the answer
    is accepted; anything else is treated as failure feedback.

    Args:
        llm: LLM instance used for evaluation.
        callbacks: Optional list of CallbackHandler instances.

    Examples:
        >>> corrector = LLMCorrector(llm=OpenAI())
        >>> passed, feedback = corrector.check(
        ...     question="What is 2+2?",
        ...     answer="4",
        ... )
        >>> passed
        True
    """

    def __init__(
        self,
        llm: LLM,
        callbacks: Optional[List[CallbackHandler]] = None,
    ) -> None:
        self.llm = llm
        self.callbacks = callbacks or []

    def check(self, question: str, answer: str) -> tuple:
        """Evaluate whether the answer is correct.

        Args:
            question: The original question.
            answer: The Agent's answer to evaluate.

        Returns:
            A tuple of (passed: bool, feedback: str).
            If passed, feedback is an empty string.
        """
        prompt = CORRECTOR_PROMPT.format(question=question, answer=answer)
        response = self.llm.generate([prompt])[0]
        if response.strip().upper().startswith("PASS"):
            return (True, "")
        return (False, response.strip())


class SelfCorrectingAgent(CallbackMixin):
    """Wrap an Agent with automatic validation and retry.

    SelfCorrectingAgent runs the wrapped Agent, validates the
    output with a Corrector, and retries with feedback if the
    answer doesn't pass. The feedback is appended to the original
    question so the Agent knows what to fix.

    Args:
        agent: Any Agent instance to wrap.
        corrector: A LLMCorrector for validating answers.
        max_retries: Maximum number of attempts (including the
            first). Default is 3.
        callbacks: Optional list of CallbackHandler instances.

    Examples:
        >>> agent = Agent(llm=llm, tools=[...])
        >>> corrector = LLMCorrector(llm=llm)
        >>> sc_agent = SelfCorrectingAgent(agent, corrector)
        >>> sc_agent.run("What is the derivative of x²?")
        '2x'
    """

    def __init__(
        self,
        agent: Agent,
        corrector: LLMCorrector,
        max_retries: int = 3,
        callbacks: Optional[List[CallbackHandler]] = None,
    ) -> None:
        self.agent = agent
        self.corrector = corrector
        self.max_retries = max_retries
        self.callbacks = callbacks or []
        # Merge callbacks into wrapped agent
        if callbacks:
            self.agent.callbacks = list(
                {id(h): h for h in self.agent.callbacks + list(callbacks)}.values()
            )

    def run(self, question: str) -> str:
        """Run the agent with self-correction, returning the best answer.

        Args:
            question: The question to answer.

        Returns:
            The final answer (after validation and possible retries).
        """
        result = self.run_with_log(question)
        return result["final_answer"]

    def run_with_log(self, question: str) -> Dict:
        """Run with self-correction and return full log.

        Args:
            question: The question to answer.

        Returns:
            Dict with:
            - ``attempts``: list of dicts with ``answer`` and ``passed`` keys
            - ``final_answer``: the answer from the last attempt
        """
        attempts = []
        current_question = question

        for i in range(self.max_retries):
            answer = self.agent.run(question=current_question)
            passed, feedback = self.corrector.check(question=question, answer=answer)

            attempts.append({"answer": answer, "passed": passed})

            if passed:
                return {"attempts": attempts, "final_answer": answer}

            # Append feedback to question for retry
            if i < self.max_retries - 1:
                current_question = (
                    f"{question}\n\n"
                    f"[Previous attempt had issues. Feedback: {feedback}]\n"
                    f"Please fix these issues and try again."
                )

        return {"attempts": attempts, "final_answer": attempts[-1]["answer"]}
