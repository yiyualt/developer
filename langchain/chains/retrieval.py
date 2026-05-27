"""RetrievalChain - end-to-end RAG pipeline.

RetrievalChain combines a VectorStore, an Embeddings model, and
an LLMChain into a complete retrieve-then-generate workflow:

1. Embed the user's question
2. Retrieve relevant documents from the VectorStore
3. Concatenate document content as context
4. Pass context + question to the LLMChain for generation

This is the core of RAG (Retrieval-Augmented Generation) —
augmenting LLM responses with external knowledge.
"""

from langchain.chains.llm_chain import LLMChain
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore


class RetrievalChain:
    """End-to-end RAG chain: retrieve relevant documents, then generate.

    Args:
        vectorstore: A VectorStore containing indexed documents.
        embeddings: An Embeddings model for encoding queries.
        llm_chain: An LLMChain whose prompt MUST include a
            ``{context}``` variable and typically also ``{question}``.
        k: Number of documents to retrieve per query. Default is 4.
        separator: String used to concatenate retrieved documents
            into the context variable. Default is ``\\n\\n``.
    """

    def __init__(
        self,
        vectorstore: VectorStore,
        embeddings: Embeddings,
        llm_chain: LLMChain,
        k: int = 4,
        separator: str = "\n\n",
    ) -> None:
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.llm_chain = llm_chain
        self.k = k
        self.separator = separator

    def run(self, question: str, **kwargs: str) -> str:
        """Execute the RAG pipeline and return the LLM's answer.

        Args:
            question: The user's question to answer.
            **kwargs: Additional input variables for the LLMChain's
                prompt template.

        Returns:
            The LLM's response string (or parsed result if the
            LLMChain has an output_parser).
        """
        # Step 1: Embed the question
        query_embedding = self.embeddings.embed_text(question)

        # Step 2: Retrieve relevant documents
        docs = self.vectorstore.similarity_search(query_embedding, k=self.k)

        # Step 3: Format context from retrieved documents
        context = self.separator.join(doc.page_content for doc in docs)

        # Step 4: Generate answer via LLMChain
        return self.llm_chain.run(question=question, context=context, **kwargs)