Async Example
=============

Concurrent LLM calls with apply_async
--------------------------------------

.. code-block:: python

    import asyncio
    import time

    from langchain import OpenAI, PromptTemplate, LLMChain

    prompt = PromptTemplate(
        input_variables=["language"],
        template="Describe {language} in one paragraph.",
    )
    chain = LLMChain(prompt=prompt, llm=OpenAI())

    input_list = [
        {"language": "Python"},
        {"language": "Rust"},
        {"language": "Go"},
    ]

    # Synchronous apply — sequential, slow
    start = time.time()
    results = chain.apply(input_list)
    sync_time = time.time() - start
    print(f"apply() took {sync_time:.2f}s")

    # Async apply — concurrent, faster
    start = time.time()
    results = asyncio.run(chain.apply_async(input_list))
    async_time = time.time() - start
    print(f"apply_async() took {async_time:.2f}s")

    # Results are in the same order as input
    for i, r in enumerate(results):
        print(f"[{input_list[i]['language']}] {r[:60]}...")

Concurrent LLM calls with agenerate
------------------------------------

.. code-block:: python

    import asyncio

    from langchain.llms import OpenAI

    llm = OpenAI()

    prompts = [
        "What is Python?",
        "What is Rust?",
        "What is Go?",
    ]

    # Synchronous — one at a time
    responses = llm.generate(prompts)

    # Async — all at once
    responses = asyncio.run(llm.agenerate(prompts))

    # Same results, same order
    assert len(responses) == 3

With output parser
------------------

.. code-block:: python

    import asyncio

    from langchain import OpenAI, PromptTemplate, LLMChain, JsonOutputParser

    prompt = PromptTemplate(
        input_variables=["topic"],
        template="Return a JSON object with 'topic' and 'description' about {topic}.",
    )
    chain = LLMChain(
        prompt=prompt,
        llm=OpenAI(),
        output_parser=JsonOutputParser(),
    )

    input_list = [{"topic": "Python"}, {"topic": "Rust"}]
    results = asyncio.run(chain.apply_async(input_list))

    for r in results:
        print(r)  # parsed dicts, not strings

Concurrent Agent runs with apply_async
---------------------------------------

.. code-block:: python

    import asyncio

    from langchain import Agent, OpenAI, CalculatorTool

    agent = Agent(llm=OpenAI(), tools=[CalculatorTool()])

    # Run multiple questions concurrently
    questions = [
        "What is 15 * 7?",
        "What is 99 + 1?",
        "What is 100 / 4?",
    ]

    answers = asyncio.run(agent.apply_async(questions))

    for q, a in zip(questions, answers):
        print(f"Q: {q}")
        print(f"A: {a}")
        print()

Each question runs in an independent ReAct loop using ``llm.agenerate()``.
Results are returned in the same order as the input questions — just like
``LLMChain.apply_async()``.