"""Tests for chat message types, ChatPromptTemplate, and generate_messages."""

from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain.prompts.chat import ChatPromptTemplate


# ── Message types ────────────────────────────────────────────────
def test_system_message():
    msg = SystemMessage("You are helpful")
    assert msg.role == "system"
    assert msg.content == "You are helpful"
    assert isinstance(msg, BaseMessage)


def test_human_message():
    msg = HumanMessage("What is Python?")
    assert msg.role == "user"
    assert msg.content == "What is Python?"


def test_ai_message():
    msg = AIMessage("Python is a language")
    assert msg.role == "assistant"
    assert msg.content == "Python is a language"


def test_message_equality():
    a = SystemMessage("hi")
    b = SystemMessage("hi")
    c = SystemMessage("bye")
    assert a == b
    assert a != c


def test_message_repr():
    msg = SystemMessage("hello")
    assert "SystemMessage" in repr(msg)
    assert "hello" in repr(msg)


# ── ChatPromptTemplate ───────────────────────────────────────────
def test_chat_prompt_format():
    template = ChatPromptTemplate([
        SystemMessage("You are a {role}"),
        HumanMessage("Explain {topic}"),
    ])
    result = template.format(role="math tutor", topic="calculus")

    assert len(result) == 2
    assert result[0].content == "You are a math tutor"
    assert result[0].role == "system"
    assert isinstance(result[0], SystemMessage)
    assert result[1].content == "Explain calculus"
    assert result[1].role == "user"
    assert isinstance(result[1], HumanMessage)


def test_chat_prompt_preserves_original():
    """Format returns new instances, original is not mutated."""
    original = SystemMessage("You are a {role}")
    template = ChatPromptTemplate([original])
    result = template.format(role="tutor")

    assert original.content == "You are a {role}"  # unchanged
    assert result[0].content == "You are a tutor"  # formatted
    assert original is not result[0]  # different instance


def test_chat_prompt_with_ai_message():
    template = ChatPromptTemplate([
        HumanMessage("Question: {q}"),
        AIMessage("Answer: {a}"),
    ])
    result = template.format(q="Hi", a="Hello!")
    assert result[0].content == "Question: Hi"
    assert result[1].content == "Answer: Hello!"
    assert isinstance(result[1], AIMessage)


# ── OpenAI generate_messages ─────────────────────────────────────
def test_generate_messages_basic():
    """generate_messages sends correct roles to the API."""
    from unittest.mock import MagicMock, patch

    with patch("langchain.llms.openai.openai.OpenAI") as mock_client:
        from langchain.llms.openai import OpenAI

        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="I am helpful"))
        ]
        mock_client.return_value.chat.completions.create.return_value = mock_completion

        llm = OpenAI(openai_api_key="sk-test")
        # Override the client with our mock
        llm._client = mock_client.return_value

        result = llm.generate_messages([[
            SystemMessage("You are helpful"),
            HumanMessage("Say hi"),
        ]])

        assert result == ["I am helpful"]
        # Verify correct roles were passed
        call_args = mock_client.return_value.chat.completions.create.call_args
        messages_sent = call_args[1]["messages"]
        assert messages_sent[0] == {"role": "system", "content": "You are helpful"}
        assert messages_sent[1] == {"role": "user", "content": "Say hi"}


def test_generate_messages_multiple_conversations():
    """generate_messages handles multiple conversation turns."""
    from unittest.mock import MagicMock, patch

    with patch("langchain.llms.openai.openai.OpenAI") as mock_client:
        from langchain.llms.openai import OpenAI

        mock_completion_1 = MagicMock()
        mock_completion_1.choices = [MagicMock(message=MagicMock(content="Hi!"))]
        mock_completion_2 = MagicMock()
        mock_completion_2.choices = [MagicMock(message=MagicMock(content="42"))]
        mock_client.return_value.chat.completions.create.side_effect = [
            mock_completion_1, mock_completion_2,
        ]

        llm = OpenAI(openai_api_key="sk-test")
        llm._client = mock_client.return_value

        results = llm.generate_messages([
            [HumanMessage("Say hi")],
            [SystemMessage("You are a calculator"), HumanMessage("2+2?")],
        ])

        assert results == ["Hi!", "42"]
        assert mock_client.return_value.chat.completions.create.call_count == 2


if __name__ == "__main__":
    import sys
    functions = [name for name in dir() if name.startswith("test_")]
    passed = 0
    failed = 0
    for func_name in sorted(functions):
        try:
            globals()[func_name]()
            print(f"  ✓ {func_name}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {func_name}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
