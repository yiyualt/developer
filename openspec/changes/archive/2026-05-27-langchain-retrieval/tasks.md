## 1. Document 基础类型与 DocumentLoader

- [x] 1.1 创建 `langchain/schema.py` — 定义 Document dataclass (page_content, metadata)
- [x] 1.2 创建 `langchain/document_loaders/__init__.py` — 导出 DocumentLoader, TextLoader, Document
- [x] 1.3 实现 `langchain/document_loaders/base.py` — DocumentLoader ABC (load() → list[Document])
- [x] 1.4 实现 `langchain/document_loaders/text.py` — TextLoader (file_path → Document with metadata["source"])

## 2. TextSplitter

- [x] 2.1 创建 `langchain/text_splitters/__init__.py` — 导出 TextSplitter
- [x] 2.2 实现 `langchain/text_splitters/base.py` — TextSplitter (chunk_size, chunk_overlap, split_text(), split_documents())

## 3. Embeddings

- [x] 3.1 创建 `langchain/embeddings/__init__.py` — 导出 Embeddings, DashScopeEmbeddings
- [x] 3.2 实现 `langchain/embeddings/base.py` — Embeddings ABC (embed_text(), embed_texts())
- [x] 3.3 实现 `langchain/embeddings/dashscope.py` — DashScopeEmbeddings (复用 .env 配置，调用 OpenAI-compatible embedding API)

## 4. VectorStore

- [x] 4.1 创建 `langchain/vectorstores/__init__.py` — 导出 VectorStore, SimpleVectorStore
- [x] 4.2 实现 `langchain/vectorstores/base.py` — VectorStore ABC (add_texts(), similarity_search(), add_documents())
- [x] 4.3 实现 `langchain/vectorstores/simple.py` — SimpleVectorStore (numpy 余弦相似度，内存存储)

## 5. RetrievalChain

- [x] 5.1 创建 `langchain/chains/retrieval.py` — RetrievalChain (vectorstore + embeddings + llm_chain + k)
- [x] 5.2 实现 RetrievalChain.run() — embed query → similarity_search → format context → LLMChain.run(context=..., question=...)

## 6. 整合与导出

- [x] 6.1 更新 `langchain/__init__.py` — 导出所有新增组件 (Document, DocumentLoader, TextLoader, TextSplitter, Embeddings, DashScopeEmbeddings, VectorStore, SimpleVectorStore, RetrievalChain)
- [x] 6.2 更新 `langchain/chains/__init__.py` — 导出 RetrievalChain
- [x] 6.3 添加 numpy 到项目依赖

## 7. Sphinx 文档

- [x] 7.1 新增 `docs/notes/retrieval-philosophy.rst` — RAG 设计哲学笔记
- [x] 7.2 新增 `docs/examples/retrieval-example.rst` — RAG 使用示例
- [x] 7.3 新增 `docs/api/document-loaders.rst`, `docs/api/text-splitters.rst`, `docs/api/embeddings.rst`, `docs/api/vectorstores.rst` — API 文档
- [x] 7.4 更新 `docs/api/index.rst` 和 `docs/examples/index.rst`, `docs/notes/index.rst` — 注册新文档页面