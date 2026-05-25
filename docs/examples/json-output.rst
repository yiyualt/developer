JSON Output Example
===================

A complete example of requesting structured JSON from an LLM and
parsing it with ``JsonOutputParser``.

.. code-block:: python

   from langchain.prompts import PromptTemplate
   from langchain.llms import OpenAI
   from langchain.chains import LLMChain
   from langchain.output_parsers import JsonOutputParser

   # Define a prompt that asks for JSON output
   prompt = PromptTemplate(
       "Return a JSON object with keys 'topic' and 'summary' "
       "about the following subject: {subject}"
   )

   # Set up LLM (reads from .env)
   llm = OpenAI(temperature=0)

   # Create chain with JSON parser
   chain = LLMChain(
       prompt=prompt,
       llm=llm,
       output_parser=JsonOutputParser(),
   )

   # Run the chain — returns a dict, not a string
   result = chain.run(subject="Python programming")
   print(result)
   # {'topic': 'Python', 'summary': 'Python is a high-level...'}

   # Now you can use result as a normal Python dict
   print(result["topic"])    # Python
   print(result["summary"])  # Python is a high-level...

Without the parser, ``chain.run()`` would return the raw string:
`````json {"topic": "Python", "summary": "..."} `````.
With the parser, it returns a usable dict.

Key Points
----------

- ``JsonOutputParser`` handles JSON in markdown code blocks and mixed text
- ``LLMChain`` with ``output_parser`` returns parsed data instead of raw strings
- Without ``output_parser``, ``LLMChain`` still returns raw strings (backward compatible)
- Use ``temperature=0`` for more deterministic, structured output