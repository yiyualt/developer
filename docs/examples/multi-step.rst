Multi-Step Chain
================

This example demonstrates SequentialChain — chaining multiple
LLMChains together so that each step's output feeds the next step.

Two-step: extract then summarize
--------------------------------

Step 1 extracts a topic from a subject, and Step 2 summarizes that
topic.

.. code-block:: python

   from langchain import PromptTemplate, OpenAI, LLMChain, SequentialChain
   from langchain.output_parsers import JsonOutputParser

   llm = OpenAI()

   # Step 1: extract topic from subject
   prompt1 = PromptTemplate(
       input_variables=["subject"],
       template="Name one topic related to {subject}. "
                "Reply in JSON: {{\"topic\": \"...\"}}",
   )
   step1 = LLMChain(prompt=prompt1, llm=llm, output_parser=JsonOutputParser())

   # Step 2: summarize the topic (receives {topic} from step 1)
   prompt2 = PromptTemplate(
       input_variables=["topic"],
       template="Write a one-line summary of {topic}.",
   )
   step2 = LLMChain(prompt=prompt2, llm=llm)

   # Chain them together
   seq = SequentialChain(
       chains=[step1, step2],
       input_variables=["subject"],
   )

   result = seq.run(subject="Python")
   # result ≈ {"subject": "Python", "topic": "Python programming",
   #           "text": "Python is a versatile programming language..."}

Three-step: extract → summarize → translate
--------------------------------------------

Adding a third step that translates the summary.

.. code-block:: python

   prompt3 = PromptTemplate(
       input_variables=["text"],
       template="Translate the following into Chinese: {text}",
   )
   step3 = LLMChain(prompt=prompt3, llm=llm)

   seq = SequentialChain(
       chains=[step1, step2, step3],
       input_variables=["subject"],
   )

   result = seq.run(subject="Python")
   # result contains keys from all three steps: topic, text (summary),
   # and text (translation) — note key collision if same output key name