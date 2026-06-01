Chat Model Example
===================

This example demonstrates Chat Model — typed messages, ChatPromptTemplate,
and ``generate_messages()``.

Creating messages
------------------

.. code-block:: python

   from langchain import SystemMessage, HumanMessage, AIMessage

   system = SystemMessage("You are a helpful math tutor.")
   user = HumanMessage("What is the derivative of x²?")
   ai = AIMessage("The derivative of x² is 2x.")

   print(system.role)   # "system"
   print(user.role)     # "user"
   print(ai.role)       # "assistant"

Using ChatPromptTemplate
-------------------------

.. code-block:: python

   from langchain import ChatPromptTemplate, SystemMessage, HumanMessage

   template = ChatPromptTemplate([
       SystemMessage("You are a {role} who speaks {language}."),
       HumanMessage("Explain {topic} in simple terms."),
   ])

   messages = template.format(
       role="math teacher",
       language="Chinese",
       topic="Pythagorean theorem",
   )

   for msg in messages:
       print(f"[{msg.role}] {msg.content}")

Calling the LLM with messages
-------------------------------

.. code-block:: python

   from langchain import OpenAI, SystemMessage, HumanMessage

   llm = OpenAI()

   response = llm.generate_messages([[
       SystemMessage("You are a helpful assistant. Answer in one sentence."),
       HumanMessage("What is machine learning?"),
   ]])
   print(response[0])

Combining ChatPromptTemplate with generate_messages
----------------------------------------------------

.. code-block:: python

   from langchain import ChatPromptTemplate, SystemMessage, HumanMessage, OpenAI

   llm = OpenAI()
   template = ChatPromptTemplate([
       SystemMessage("You are a {expertise} expert."),
       HumanMessage("Summarize {field} in one paragraph."),
   ])

   messages = template.format(expertise="Python", field="asyncio")
   result = llm.generate_messages([messages])
   print(result[0])
