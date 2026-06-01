Retrieval Example
=================

This example demonstrates RAG (Retrieval-Augmented Generation) —
augmenting LLM answers with external document knowledge.

End-to-end RAG pipeline
------------------------

.. code-block:: python

   from langchain import (
       TextLoader, TextSplitter, LocalEmbeddings,
       SimpleVectorStore, RetrievalChain, PromptTemplate,
       OpenAI, LLMChain, Document,
   )

   # Step 1: Load documents
   loader = TextLoader("data/knowledge.txt")
   docs = loader.load()

   # Step 2: Split into chunks
   splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
   chunks = splitter.split_documents(docs)

   # Step 3: Embed and store (LocalEmbeddings runs offline, no API key needed)
   embeddings_model = LocalEmbeddings()
   texts = [c.page_content for c in chunks]
   vectors = embeddings_model.embed_texts(texts)

   vectorstore = SimpleVectorStore()
   vectorstore.add_documents(chunks, vectors)

   # Step 4: Build RetrievalChain
   prompt = PromptTemplate(
       input_variables=["context", "question"],
       template="Use the following context to answer the question.\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n\nAnswer:",
   )

   chain = LLMChain(prompt=prompt, llm=OpenAI())
   rag = RetrievalChain(
       vectorstore=vectorstore,
       embeddings=embeddings_model,
       llm_chain=chain,
       k=3,
   )

   # Step 5: Ask a question
   answer = rag.run(question="What is LangChain?")
   print(answer)

Using DashScopeEmbeddings
--------------------------

If your DashScope account has embedding API access, you can use
``DashScopeEmbeddings`` instead of ``LocalEmbeddings``. It shares
the same ``.env`` configuration as the LLM:

.. code-block:: python

   from langchain import DashScopeEmbeddings

   embeddings_model = DashScopeEmbeddings()  # Uses LLM_API_KEY from .env
   # Rest of the pipeline is identical

Customizing the retrieval
--------------------------

Adjust ``k`` (number of retrieved documents) and ``separator``
(how chunks are joined as context):

.. code-block:: python

   rag = RetrievalChain(
       vectorstore=vectorstore,
       embeddings=embeddings_model,
       llm_chain=chain,
       k=2,              # Only retrieve top 2 chunks
       separator="---",  # Use "---" between chunks
   )

Loading multiple files
----------------------

Load several text files and merge their chunks:

.. code-block:: python

   docs = []
   for path in ["data/chapter1.txt", "data/chapter2.txt"]:
       docs.extend(TextLoader(path).load())

   chunks = splitter.split_documents(docs)
   vectors = embeddings_model.embed_texts([c.page_content for c in chunks])
   vectorstore.add_documents(chunks, vectors)