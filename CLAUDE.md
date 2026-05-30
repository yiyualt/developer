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

已完成（19 个版本）：
1. **v0.0.1 Core Primitives** — PromptTemplate, LLM ABC, LLMChain
2. **OpenAI LLM** — DashScope/glm-5.1 连接，.env 配置
3. **OutputParser** — OutputParser ABC, JsonOutputParser, ListOutputParser
4. **SequentialChain** — 多步串联，key-based 数据流，LLMChain.output_keys
5. **Agent (ReAct)** — Tool ABC, Agent, AgentOutputParser, Calculator/Search/PythonREPL
6. **Memory** — Memory ABC, ConversationBufferMemory, ConversationBufferWindowMemory
7. **Retrieval / RAG** — Document, DocumentLoader, TextLoader, TextSplitter, Embeddings, VectorStore, RetrievalChain
8. **Router Chain** — RouterChain ABC, LLMRouterChain, ChainDestination, 动态注入模式
9. **ConversationSummaryMemory** — LLM 增量摘要压缩
10. **Callback / Tracing** — CallbackHandler ABC, StdOutCallbackHandler, 回调集成
11. **Streaming** — LLM stream(), LLMChain/Agent stream(), on_llm_new_token
12. **Async / 并发** — LLM agenerate(), LLMChain apply_async(), asyncio.gather
13. **AgentTool** — Agent 包装为 Tool，递归组合性
14. **PlanAndExecuteAgent** — 目标 → 计划 → 逐步执行
15. **@tool 装饰器** — 函数自动转为 Tool 实例
16. **Agent Orchestration** — MultiAgentOrchestrator, SequentialAgentChain
17. **Chat Model** — SystemMessage/HumanMessage/AIMessage, ChatPromptTemplate, generate_messages()
18. **Memory↔Chat Bridge** — Memory.load_messages() 返回消息列表
19. **Self-Correction** — LLMCorrector, SelfCorrectingAgent
20. **Callback Consistency** — CallbackMixin 提取，全组件统一回调支持

## 架构约定

**所有新模块必须遵守以下规则，保持代码库一致性：**

### 回调系统
- 任何需要可观察性的组件（Agent、Chain、Tool 等）**必须**：
  1. 继承 `CallbackMixin`（`from langchain.callbacks.mixin import CallbackMixin`）
  2. 构造函数接受 `callbacks: Optional[List[CallbackHandler]] = None` 参数
  3. 在 `__init__` 中写 `self.callbacks = callbacks or []`
  4. 关键执行点用 `self._fire("event_name", **kwargs)` 发送事件
- CallbackMixin 已提供 `_fire` 方法，**不要**自己重新实现
- 如果组件包装了另一个有回调的组件，**必须**将 callbacks 合并传递进去，让事件流不断：

  ```python
  if callbacks:
      self.wrapped.callbacks = list(
          {id(h): h for h in self.wrapped.callbacks + list(callbacks)}.values()
      )
  ```

### Tool 事件归属
- `on_tool_start` / `on_tool_end` / `on_error` 由 **Tool.run()** 层负责 fire
- **不要**在 Agent 或其他调用方重复 fire 这些事件

### 文档
- 每个重要功能**必须**有：
  - `docs/notes/<feature>-philosophy.rst` — 设计理念（为什么这样设计）
  - `docs/examples/<feature>-example.rst` — 可运行的代码示例
  - 在 `docs/notes/index.rst` 和 `docs/examples/index.rst` 的 toctree 中注册
- 全量构建文档用 `rm -rf docs/_build && sphinx-build -b html docs/ docs/_build/html`

### 测试
- 每个新功能**必须**有对应的 `tests/test_<feature>.py`
- 测试用 `FakeLLM` 模拟 LLM 调用，不依赖真实 API
- 用 `RecordingHandler`（实现 `CallbackHandler`）验证回调事件

### API 风格
- Agent 类必须暴露 `run(question) -> str` 和 `run_with_log(question) -> dict`
- 返回的 dict 必须包含 `final_answer` 键
- 构造函数参数默认值优先使用空列表/空字符串（`[]`, `""`），不用 `None` 除非语义上有区别

### Schema / 数据对象
- 基础数据结构放在 `langchain/schema.py`（当前有 `Document`、`BaseMessage`、`SystemMessage`、`HumanMessage`、`AIMessage`）

## OpenSpec 工作流

- 使用 openspec CLI 管理变更（从项目根目录运行）
- 流程：propose → apply → archive
- 归档前必须 sync delta specs 到 main specs
- 变更目录在 `openspec/changes/`（不是 `docs/openspec/changes/`）