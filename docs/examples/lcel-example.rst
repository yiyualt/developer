LCEL Example
=============

Declarative chain composition with the ``|`` operator.

Basic pipeline
--------------

.. code-block:: python

   from langchain import PromptTemplate, OpenAI

   chain = PromptTemplate("Tell me about {topic} in one sentence.") | OpenAI()
   result = chain.invoke({"topic": "Python"})
   print(result)

With output parser
------------------

.. code-block:: python

   from langchain import PromptTemplate, OpenAI, JsonOutputParser

   chain = (
       PromptTemplate("Return JSON: {{\"topic\": \"{topic}\", \"summary\": \"...\"}}")
       | OpenAI()
       | JsonOutputParser()
   )
   data = chain.invoke({"topic": "Python"})
   print(data["summary"])

Composing multiple chains
--------------------------

Each chain is a Runnable — you can compose them too:

.. code-block:: python

   from langchain import PromptTemplate, OpenAI

   llm = OpenAI()

   # Create two independent chains
   extract_chain = PromptTemplate("Extract key facts from: {text}") | llm
   summarize_chain = PromptTemplate("Summarize: {facts}") | llm

   # Run them separately
   facts = extract_chain.invoke({"text": "Python was created in 1991..."})
   summary = summarize_chain.invoke({"facts": facts})
   print(summary)

Type compatibility
------------------

A ``|`` chain requires each step's output type to match the next step's
input type:

.. code-block:: text

   PromptTemplate → str        (input: dict)
   LLM            → str        (input: str)
   OutputParser   → Any        (input: str)

   Valid:   PromptTemplate | LLM | OutputParser  (dict → str → str → Any)
   Invalid: PromptTemplate | PromptTemplate      (PromptTemplate expects dict, not str)

Comparison: LCEL vs LLMChain
-----------------------------

.. code-block:: python

   # Before: LLMChain (imperative)
   from langchain import LLMChain
   chain = LLMChain(
       prompt=PromptTemplate("Say {word}"),
       llm=OpenAI(),
   )
   chain.run(word="hello")

   # After: LCEL (declarative)
   chain = PromptTemplate("Say {word}") | OpenAI()
   chain.invoke({"word": "hello"})
