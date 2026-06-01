Streaming Example
================

Token-level streaming with LLMChain
------------------------------------

.. code-block:: python

    from langchain import OpenAI, PromptTemplate, LLMChain, StdOutCallbackHandler

    prompt = PromptTemplate(
        input_variables=["topic"],
        template="Tell me a short story about {topic}.",
    )
    chain = LLMChain(
        prompt=prompt,
        llm=OpenAI(),
        callbacks=[StdOutCallbackHandler()],
    )

    # Blocking call — waits for the full response
    result = chain.run(topic="a brave cat")
    print(f"\nFull response: {result}")

    # Streaming call — tokens appear one at a time
    print("\nStreaming:")
    for token in chain.stream(topic="a brave cat"):
        pass  # StdOutCallbackHandler already prints each token

Step-level streaming with Agent
-------------------------------

.. code-block:: python

    from langchain import OpenAI, Agent, CalculatorTool, StdOutCallbackHandler

    agent = Agent(
        llm=OpenAI(),
        tools=[CalculatorTool()],
        callbacks=[StdOutCallbackHandler()],
    )

    # Blocking call — returns final answer only
    answer = agent.run(question="What is 2 + 3?")

    # Streaming call — shows each reasoning step
    for event in agent.stream(question="What is 2 + 3?"):
        print(f"  [{event['type']}] {event['content']}")

Performance note
----------------

Streaming does not make the LLM faster. A streaming call takes the
same wall-clock time as ``run()``. The benefit is perceived
responsiveness — the user sees progress instead of waiting for a
blank screen.

.. code-block:: python

    import time

    start = time.time()
    chain.run(topic="Python")
    blocking_time = time.time() - start

    start = time.time()
    tokens = list(chain.stream(topic="Python"))
    streaming_time = time.time() - start

    print(f"Blocking: {blocking_time:.2f}s")
    print(f"Streaming: {streaming_time:.2f}s")
    # Both take roughly the same time, but streaming shows progress