"""Tests for LCEL — Runnable, | operator, composable pipelines."""

from langchain.runnables import Runnable, RunnableSequence


# ── Runnable ABC ────────────────────────────────────────────────
def test_runnable_subclass():
    """Subclassing Runnable requires invoke."""
    class MyRunnable(Runnable):
        def invoke(self, input, **kwargs):
            return f"processed: {input}"

    r = MyRunnable()
    assert r.invoke("hello") == "processed: hello"


# ── Pipe operator ───────────────────────────────────────────────
def test_pipe_creates_sequence():
    """a | b returns RunnableSequence."""
    class A(Runnable):
        def invoke(self, input, **kwargs): return input.upper()
    class B(Runnable):
        def invoke(self, input, **kwargs): return f"[{input}]"

    seq = A() | B()
    assert isinstance(seq, RunnableSequence)
    assert seq.invoke("hello") == "[HELLO]"


def test_three_step_pipe():
    """a | b | c executes in order."""
    class A(Runnable):
        def invoke(self, input, **kwargs): return input + "A"
    class B(Runnable):
        def invoke(self, input, **kwargs): return input + "B"
    class C(Runnable):
        def invoke(self, input, **kwargs): return input + "C"

    result = (A() | B() | C()).invoke("")
    assert result == "ABC"


# ── RunnableSequence ────────────────────────────────────────────
def test_sequence_single_step():
    """Single step returns its output."""
    class Echo(Runnable):
        def invoke(self, input, **kwargs): return input
    assert RunnableSequence(Echo()).invoke("x") == "x"


# ── PromptTemplate as Runnable ──────────────────────────────────
def test_prompt_template_invoke():
    """PromptTemplate.invoke() formats template from dict."""
    from langchain.prompts.prompt import PromptTemplate
    p = PromptTemplate("Hello {name}")
    assert p.invoke({"name": "World"}) == "Hello World"
    assert isinstance(p, Runnable)


# ── LLM as Runnable ─────────────────────────────────────────────
def test_llm_invoke():
    """LLM.invoke() generates from a string."""
    from langchain.llms.base import LLM

    class FakeLLM(LLM):
        def _generate(self, prompts):
            return [f"response to: {p}" for p in prompts]

    llm = FakeLLM()
    assert isinstance(llm, Runnable)
    result = llm.invoke("hello")
    assert "response to: hello" == result


# ── OutputParser as Runnable ────────────────────────────────────
def test_output_parser_invoke():
    """OutputParser.invoke() parses text."""
    from langchain.output_parsers.base import OutputParser

    class FakeParser(OutputParser):
        def parse(self, text): return {"parsed": text}

    parser = FakeParser()
    assert isinstance(parser, Runnable)
    assert parser.invoke("hello") == {"parsed": "hello"}


# ── End-to-end LCEL ─────────────────────────────────────────────
def test_lcel_pipeline():
    """prompt | llm runs end-to-end."""
    from langchain.prompts.prompt import PromptTemplate
    from langchain.llms.base import LLM

    class FakeLLM(LLM):
        def _generate(self, prompts):
            return [f"LLM says: {p}" for p in prompts]

    prompt = PromptTemplate("Say {word}")
    llm = FakeLLM()

    chain = prompt | llm
    result = chain.invoke({"word": "hello"})
    assert result == "LLM says: Say hello"


def test_lcel_with_parser():
    """prompt | llm | parser end-to-end."""
    from langchain.prompts.prompt import PromptTemplate
    from langchain.llms.base import LLM
    from langchain.output_parsers.base import OutputParser

    class FakeLLM(LLM):
        def _generate(self, prompts): return [p.upper() for p in prompts]

    class FakeParser(OutputParser):
        def parse(self, text): return {"result": text}

    chain = PromptTemplate("{x}") | FakeLLM() | FakeParser()
    result = chain.invoke({"x": "hello"})
    assert result == {"result": "HELLO"}


if __name__ == "__main__":
    import sys
    fns = [n for n in dir() if n.startswith("test_")]
    p = f = 0
    for fn in sorted(fns):
        try:
            globals()[fn]()
            print(f"  ✓ {fn}")
            p += 1
        except Exception as e:
            print(f"  ✗ {fn}: {e}")
            f += 1
    print(f"\n{p} passed, {f} failed")
    sys.exit(1 if f else 0)
