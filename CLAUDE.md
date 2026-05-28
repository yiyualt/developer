# LangChain 项目指引

## 项目目标

模拟 LangChain 的真实发展历史，在构建过程中体验设计、理念和技术的演进。
不是照抄最终版 LangChain，而是按时间线还原每个版本的增量变化，
在每一步中感受"为什么这样设计"的决策过程。

## 文档风格

PyTorch 风格文档体系：
- Sphinx + sphinx-book-theme 构建
- 四层结构：tutorials / notes / examples / api
- Notes culture：每个重要设计决策都有 philosophy 文档
- 全量构建时必须 `rm -rf docs/_build && sphinx-build`，避免增量构建导致侧边栏缺失

## LLM 配置

- Provider: DashScope (阿里云)，OpenAI-compatible API
- Model: glm-5.1
- 配置在 .env (gitignored): LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
- Git push 用 HTTPS + 代理 (127.0.0.1:7897)

## 版本演进路线

已完成：
1. **v0.0.1 Core Primitives** — PromptTemplate, LLM ABC, LLMChain
2. **OpenAI LLM** — DashScope/glm-5.1 连接，.env 配置
3. **OutputParser** — OutputParser ABC, JsonOutputParser, ListOutputParser
4. **SequentialChain** — 多步串联，key-based 数据流，LLMChain.output_keys
5. **Agent (ReAct)** — Tool ABC, Agent, AgentOutputParser, Calculator/Search/PythonREPL
6. **Memory** — Memory ABC, ConversationBufferMemory, ConversationBufferWindowMemory, LLMChain/Agent 集成
7. **Retrieval / RAG** — Document, DocumentLoader, TextLoader, TextSplitter, Embeddings, DashScopeEmbeddings, LocalEmbeddings, VectorStore, SimpleVectorStore, RetrievalChain
8. **Router Chain** — RouterChain ABC, LLMRouterChain, ChainDestination, Dynamic Option Injection 模式
9. **ConversationSummaryMemory** — LLM 增量摘要压缩, Agent 保存完整推理过程
10. **Callback / Tracing** — CallbackHandler ABC, StdOutCallbackHandler, LLMChain/Agent/Tool 回调集成
11. **Streaming** — LLM stream() token 级流式输出, LLMChain/Agent stream() 方法, on_llm_new_token 钩子

下一步（按 LangChain 历史演进顺序）：
12. **Async / 并发** — LLM agenerate() + AsyncOpenAI, LLMChain apply_async(), asyncio.gather 并发

## OpenSpec 工作流

- 使用 openspec CLI 管理变更（从项目根目录运行）
- 流程：propose → apply → archive
- 归档前必须 sync delta specs 到 main specs
- 变更目录在 `openspec/changes/`（不是 `docs/openspec/changes/`）