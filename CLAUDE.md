# LangChain → LangGraph 项目指引

## 项目目标第一阶段（已完成）

模拟 LangChain 的真实发展历史，从 v0.0.1 到 v0.0.27，构建过程中体验设计、
理念和技术的演进。已完成 27 个版本，打 tag `v0.0.27-langchain-final`。

## 项目目标 —— 第二阶段：LangGraph

从当前 LangChain 代码基础上，模拟 **LangGraph** 的真实发展历史。
LangGraph 是 LangChain 的"低层编排框架"——从高层的 Chain/Agent 逻辑
下沉到低层的图执行、状态管理、持久化、Human-in-the-Loop。

核心差异：
- LangChain: "这个 Chain 怎么组合？" "这个 Agent 怎么推理？"
- LangGraph: "计算图怎么执行？" "状态怎么持久化？" "节点间怎么流数据？"

分支: `langgraph`（当前），`main` 分支保存完整的 LangChain 工作。

## LangGraph 演进路线

从真实 LangGraph 的历史出发：

1. **StateGraph** — 状态图核心：Node + Edge + State，编译为 Pregel-style 执行器
2. **Checkpoint** — 持久化状态快照，支持 pause/resume/retry
3. **Streaming** — 图执行时流式输出中间状态
4. **Human-in-the-Loop** — 中断执行，人工介入后恢复
5. **Conditional Edges** — 基于状态的动态路由
6. **Subgraphs** — 图的嵌套组合
7. **Agent as Graph** — 用 Graph 重新实现 Agent 循环
8. **ToolNode** — 将 Tool 包装为图的节点

## 文档风格

PyTorch 风格文档体系：
- Sphinx + sphinx-book-theme 构建
- 四层结构：tutorials / notes / examples / api
- Notes culture：每个重要设计决策都有 philosophy 文档
- 全量构建时必须 `rm -rf docs/_build && sphinx-build`，避免增量构建导致侧边栏缺失
- **全部英文**：所有 .rst 文档内容必须是英文，不可混用中文

## LLM 配置

- Provider: DashScope (阿里云)，OpenAI-compatible API
- Model: glm-5.1
- 配置在 .env (gitignored): LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
- Git push 用 HTTPS + 代理 (127.0.0.1:7897)

## LangChain 版本（已完成，tag: v0.0.27-langchain-final）

共 27 个版本，覆盖 Chain → Agent → Memory → RAG → Router → Streaming →
Async → AgentTool → PlanExecute → Orchestration → Chat Model →
Self-Correction → Callback → LCEL → Function Calling → Middleware 栈。详见 `main` 分支。

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

## 实施后校验（交付前必须执行）

每次 `openspec-apply-change` 完成后、告知用户之前，**必须**执行以下校验：

### async 真伪验证
- 如果新增了 `async def` 方法，确认它内部**实际调用了 await**，而非同步调用包装成 async
- 检查：`agenerate_messages()` / `agenerate()` / `apply_async()` 等 async 方法必须调用对应的 async LLM 方法，**不能**内部调 sync 方法而让 `asyncio.gather` 空转
- 反例：`async def _arun_loop` 内部调用 `self.llm.generate_messages()`（sync） → asyncio.gather 不并发

### 代码质量
- 搜索新代码中的死代码：`grep -n "def _" <file>` 检查是否有未被调用的私有方法
- 搜索重复逻辑：如果两个方法逻辑完全相同（逐行比对），必须合并
- 反例：`_run_loop` 和 `_arun_loop` 完全相同的 ReAct 循环 → 应该用一个带参数的方法

### 文档完整性
- 检查所有示例代码**必须可运行**——不能有 `...` 占位符、未定义的变量、伪代码
  - 检查命令：`grep -n "\.\.\." docs/examples/*.rst | grep -v "output\|truncat\|summary\|..."`（需要人工判断哪些是合法截断）
  - 反例：`tools=[...]`、`agent.run("...")`、`# ... (setup steps)` — 必须替换为真实代码
- 检查 toctree 是否已注册新文件：`grep <new-file> docs/notes/index.rst docs/examples/index.rst`

### 测试覆盖
- 运行新测试文件：`PYTHONPATH=. python tests/test_<feature>.py`，确保全部通过
- 运行所有已有测试套件，确认零回归
- 如果新增了 async 方法，测试**必须**实际验证并发（检查 `asyncio.gather` 被调用、结果顺序正确）

### 文档完整性
- 检查是否创建/更新了对应的 notes 和 examples 文件
- 检查 toctree 是否已注册
- 检查 docs 是否已重建

## OpenSpec 工作流

- 使用 openspec CLI 管理变更（从项目根目录运行）
- 流程：propose → apply → archive
- 归档前必须 sync delta specs 到 main specs
- 变更目录在 `openspec/changes/`（不是 `docs/openspec/changes/`）