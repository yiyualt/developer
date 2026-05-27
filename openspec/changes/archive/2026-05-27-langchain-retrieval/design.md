## Context

LangChain 已完成 6 个版本的演进（Core Primitives → OpenAI → OutputParser → SequentialChain → Agent → Memory），目前具备 prompt+llm=chain 的基本组合能力、多步串联、Agent 自主执行、对话记忆。但所有 Chain 和 Agent 都只能依赖 LLM 的训练知识，无法访问外部文档。

真实 LangChain 在 2022 年末引入 RAG，这是从"纯推理"走向"推理+检索"的关键跃迁。本项目按历史时间线还原这一步。

当前技术栈：
- DashScope (OpenAI-compatible API) 作为 LLM provider
- Memory 为纯内存实现（ConversationBufferMemory / ConversationBufferWindowMemory）
- Agent 通过 ReAct 循环调用 Tool
- 无外部向量数据库依赖

## Goals / Non-Goals

**Goals:**
- 实现最小但完整的 RAG 流程：文档加载 → 分块 → 嵌入 → 存储 → 检索 → 生成
-还原早期 LangChain 的设计决策（简单优先，而非生产级）
- DocumentLoader ABC + TextLoader 实现
- TextSplitter（固定字符数切割，早期 LC 的做法）
- Embeddings ABC + DashScope embedding 实现
- VectorStore ABC + SimpleVectorStore（numpy 余弦相似度，零外部依赖）
- RetrievalChain：组合 retriever + prompt + LLM 的端到端链

**Non-Goals:**
- 递归切割器（RecursiveCharacterTextSplitter）— 这是后来的演进
- 元数据过滤、hybrid search — 生产级特性
- FAISS / ChromaDB 集成 — 后续版本考虑
- PDF/HTML 等复杂格式加载器 — 先做纯文本
- 文档持久化到磁盘 — 先做内存存储

## Decisions

### Decision 1: SimpleVectorStore (numpy) 而非 FAISS

**选择**: numpy 纯 Python 实现余弦相似度搜索
**替代**: FAISS（真实 LangChain 早期选择）
**理由**: 项目目标是"感受设计决策"，不是生产部署。numpy 实现：
- 让人看清向量搜索的本质（embed → store → cosine search）
- 零外部依赖，macOS 上无安装问题
- 与早期 LC 的"简单优先"理念一致
- FAISS 安装复杂度会阻碍教学体验

### Decision 2: DashScope Embedding API

**选择**: 通过 DashScope 的 OpenAI-compatible embedding endpoint 生成向量
**替代**: 本地模型（sentence-transformers）
**理由**:
- 项目已有 DashScope 连接基础设施，复用现有配置
- 无需额外安装本地模型
- OpenAI-compatible API 格式统一，Embeddings 实现更简洁

### Decision 3: 固定长度 TextSplitter

**选择**: 按固定字符数切割，支持 overlap
**替代**: 递归切割器、语义切割
**理由**: 还原早期 LC 的做法。固定长度切割是 v1，递归切割是后来的改进。
通过简单切割先暴露问题（句子被切断），再在后续版本引入递归切割解决。

### Decision 4: RetrievalChain 作为独立 Chain

**选择**: RetrievalChain 是独立类，不继承 LLMChain
**替代**: 让 LLMChain 支持 retriever 参数
**理由**: RetrievalChain 的执行流程不同于 LLMChain（先检索再生成），
独立类更清晰。同时 LLMChain 只需微调 — prompt 模板可以包含 `{context}` 变量，
但检索逻辑不应混入 LLMChain 内部。

## Risks / Trade-offs

- **[SimpleVectorStore 性能]** → 数万级文档搜索会慢，但教学场景下文档量小，暂可接受。后续版本可引入 FAISS。
- **[Embedding API 依赖]** → DashScope API 不可用时整个 RAG 流程失效 → Embeddings ABC 设计允许后续切换到本地模型。
- **[固定切割质量]** → 可能切断句子边界，影响检索质量 → 这正是历史演进要暴露的问题，后续引入 RecursiveSplitter 解决。
- **[RetrievalChain 与 Memory 整合]** → 当前 Memory 只存 Human/AI 对话，不存检索文档 → 先不整合，后续 Agent Memory 版本解决。