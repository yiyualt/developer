"""ChatPromptTemplate — compose structured message sequences.

While PromptTemplate works with plain strings, ChatPromptTemplate
works with typed messages (SystemMessage, HumanMessage, AIMessage).
Each message's content is a template string that supports
``{variable}`` substitution.
"""

from typing import List

from langchain.schema import BaseMessage


class ChatPromptTemplate:
    """A template that formats into a list of typed chat messages.

    ChatPromptTemplate accepts a list of message instances whose
    ``content`` may contain ``{variable}`` placeholders. When
    ``format()`` is called, each message's content is formatted
    with the provided values, and a new list of messages is
    returned. The original template messages are not modified.

    Args:
        messages: A list of message instances serving as templates.
            Each message's ``content`` string may include
            ``{variable}`` placeholders.

    Examples:
        >>> template = ChatPromptTemplate([
        ...     SystemMessage("You are a {role}"),
        ...     HumanMessage("Explain {topic}"),
        ... ])
        >>> msgs = template.format(role="math tutor", topic="calculus")
        >>> msgs[0].content
        'You are a math tutor'
        >>> msgs[1].content
        'Explain calculus'
    """

    def __init__(self, messages: List[BaseMessage]) -> None:
        self.messages = messages

    def format(self, **kwargs: str) -> List[BaseMessage]:
        """Format all message templates with the provided values.

        Each message's ``content`` string is formatted using
        Python's ``str.format()``. The original messages are
        preserved — new message instances are returned.

        Args:
            **kwargs: Values for ``{variable}`` placeholders in
                message content strings.

        Returns:
            A list of new message instances with formatted content.
        """
        formatted: List[BaseMessage] = []
        for msg in self.messages:
            formatted_content = msg.content.format(**kwargs)
            formatted.append(msg.__class__(content=formatted_content))
        return formatted
