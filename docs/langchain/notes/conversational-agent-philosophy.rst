Conversational Agent Philosophy
===============================

Agent 是最早的 Agent 实现。它工作得很好——但它的世界是字符串的。
ConversationalAgent 是第一个原生于消息类型的 Agent。它不只是
"Agent + Memory"，它是用 Chat Model 的消息体系重新实现的 ReAct。

String world vs Message world
------------------------------

.. code-block:: text

   Agent (string):                     ConversationalAgent (message):

   Memory.load_context()               Memory.load_messages()
   → "Human: hi\nAI: hello"            → [HumanMessage("hi"),
                                          AIMessage("hello")]

   PromptTemplate.format()             ChatPromptTemplate
   → 一个字符串                          → [SystemMessage(...),
                                          HumanMessage(...)]

   LLM.generate([str])                 LLM.generate_messages([[msg]])
   → role 固定为 "user"                 → role 正确传递

The system prompt as a SystemMessage
-------------------------------------

In Agent, the system prompt is part of the template string:

.. code-block:: python

   # Agent: system prompt 混在模板里
   REACT_PROMPT = \"\"\"You are an agent. Use tools: {tools}...\"\"\"

In ConversationalAgent, it's a first-class SystemMessage:

.. code-block:: python

   # ConversationalAgent: system prompt 是独立消息
   messages = [
       SystemMessage("You are a helpful math tutor."),
       *memory.load_messages(),
       HumanMessage("What is the derivative of x²?"),
   ]

This separation matters because LLMs are trained to respond
differently to system vs user messages. The system message sets
the assistant's role and constraints; the user message is the
actual instruction.

Why not just modify Agent?
---------------------------

The ReAct loop core is fundamentally different:

- Agent: builds a string, calls ``generate(str)``
- ConversationalAgent: builds a message list, calls
  ``generate_messages([[msg]])``

Merging them would mean branching on a flag everywhere —
``if use_messages else``. Two independent classes, each focused on
one paradigm, is simpler.

What's next
-----------

- ChatLLMChain: a Chain that natively works with messages
- ToolMessage: for tools that need structured tool-call messages
- Streaming with messages: on_llm_new_token for generate_messages()
