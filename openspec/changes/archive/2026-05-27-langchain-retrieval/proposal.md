## Why

LLM 的知识受限于训练数据，无法回答涉及私有文档或实时信息的问题。
RAG (Retrieval-Augmented Generation) 是 LangChain 最重要的演进之一 —
让 Chain 从"纯推理"走向"推理 + 外部知识检索"。
这还原了 LangChain 2022 年末引入 DocumentLoader、VectorStore、RetrievalChain 的历史时刻。

## What Changes

- 新增 **DocumentLoader ABC** 及 TextLoader 实现 — 加载外部文档为结构化文本
- 新增 **TextSplitter** — 将长文档切割为可检索的文本块
- 新增 **VectorStore ABC** 及 SimpleVectorStore 实现 — 存储与检索文本嵌入
- 新增 **Embeddings ABC** 及 DashScope embedding 实现 — 文本转向量
- 新增 **RetrievalChain** — 组合 retriever + prompt + LLM 的端到端 RAG 链
- 更新 **LLMChain** — 支持 context 变量注入（retriever 返回的文档）

## Capabilities

### New Capabilities
- `document-loader`: 文档加载抽象与纯文本加载实现
- `text-splitter`: 文档切割为可检索的文本块
- `vector-store`: 向量存储与相似度检索
- `embeddings`: 文本嵌入（向量生成）抽象与 DashScope 实现
- `retrieval-chain`: 端到端 RAG 链（retrieve → inject → generate）

### Modified Capabilities
- `llm-chain`: 支持 context 变量注入，使 LLMChain 能接收检索结果

## Impact

- 新增 Python 模块: `langchain/document_loaders/`, `langchain/text_splitters/`, `langchain/vectorstores/`, `langchain/embeddings/`
- 更新 `langchain/chains/` — 新增 RetrievalChain，LLMChain 可能微调
- 新增依赖: `numpy` (SimpleVectorStore 余弦相似度计算), DashScope embedding API 调用
- 更新 `langchain/__init__.py` — 导出新组件
- 新增 Sphinx 文档: notes (philosophy), examples, api