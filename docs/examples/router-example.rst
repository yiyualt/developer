Router Example
==============

This example demonstrates RouterChain — dynamically selecting
which Chain to execute based on the user's question.

Multi-prompt routing (different LLMChain prompts)
----------------------------------------------------

The simplest Router use case: route questions to different
prompt templates, each specialized for a different domain.

.. code-block:: python

   from langchain import (
       LLMRouterChain, ChainDestination, LLMChain, OpenAI,
       PromptTemplate,
   )

   # Create specialized prompts for different domains
   physics_prompt = PromptTemplate(
       input_variables=["question"],
       template="You are a physics expert. Answer precisely: {question}",
   )
   math_prompt = PromptTemplate(
       input_variables=["question"],
       template="You are a math tutor. Solve step by step: {question}",
   )
   general_prompt = PromptTemplate(
       input_variables=["question"],
       template="Answer this question concisely: {question}",
   )

   llm = OpenAI()

   # Create destinations
   physics_dest = ChainDestination(
       name="physics",
       description="For questions about physics, mechanics, electricity, thermodynamics",
       chain=LLMChain(prompt=physics_prompt, llm=llm),
   )
   math_dest = ChainDestination(
       name="math",
       description="For mathematical calculations and problem solving",
       chain=LLMChain(prompt=math_prompt, llm=llm),
   )
   general_dest = ChainDestination(
       name="general",
       description="For general knowledge questions that don't need specialized expertise",
       chain=LLMChain(prompt=general_prompt, llm=llm),
   )

   # Build the router
   router = LLMRouterChain(
       llm=llm,
       destinations=[physics_dest, math_dest],
       default_destination=general_dest,
   )

   # Ask different questions — the router selects the right chain
   print(router.run(question="What is Newton's second law?"))
   # → Router selects "physics", physics_prompt is used

   print(router.run(question="Calculate 15% of 200"))
   # → Router selects "math", math_prompt is used

   print(router.run(question="What color is the sky?"))
   # → Router selects "general", general_prompt is used (or fallback)

Routing to a RetrievalChain
----------------------------

Router can route to any Chain type, including RetrievalChain.
This lets you automatically decide whether a question needs
document retrieval or can be answered from general knowledge.

.. code-block:: python

   from langchain import (
       LLMRouterChain, ChainDestination, LLMChain, RetrievalChain,
       OpenAI, PromptTemplate, LocalEmbeddings, SimpleVectorStore,
       TextLoader, TextSplitter,
   )

   # Set up a RetrievalChain from sample documents
   loader = TextLoader("data/sample.txt")
   documents = loader.load()
   splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
   chunks = splitter.split_documents(documents)
   embeddings = LocalEmbeddings()
   vectorstore = SimpleVectorStore()
   vectorstore.add_documents(chunks, embeddings)
   rag_chain = RetrievalChain(
       vectorstore=vectorstore,
       embeddings=LocalEmbeddings(),
       llm_chain=LLMChain(prompt=rag_prompt, llm=OpenAI()),
       k=3,
   )

   # General QA chain for questions that don't need documents
   general_chain = LLMChain(
       prompt=PromptTemplate(
           input_variables=["question"],
           template="Answer this question from general knowledge: {question}",
       ),
       llm=OpenAI(),
   )

   # Router chooses between retrieval and general knowledge
   router = LLMRouterChain(
       llm=OpenAI(),
       destinations=[
           ChainDestination(
               name="retrieval",
               description="For questions about specific documents, policies, or internal knowledge",
               chain=rag_chain,
           ),
       ],
       default_destination=ChainDestination(
           name="general",
           description="For general knowledge questions",
           chain=general_chain,
       ),
   )

   # Questions about documents → routed to RetrievalChain
   print(router.run(question="What is the company refund policy?"))

   # General questions → routed to LLMChain (default)
   print(router.run(question="What is Python?"))