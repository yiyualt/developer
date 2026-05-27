## 1. 核心组件实现

- [x] 1.1 创建 `langchain/chains/router.py` — ChainDestination dataclass (name, description, chain)
- [x] 1.2 实现 RouterChain ABC — route() + run() 方法
- [x] 1.3 实现 LLMRouterChain — LLM + JsonOutputParser 路由决策，prompt 自动构建，default_destination fallback
- [x] 1.4 实现 LLMRouterChain.run() — route() → destinations[name].chain.run(question=question)

## 2. 整合与导出

- [x] 2.1 更新 `langchain/__init__.py` — 导出 RouterChain, LLMRouterChain, ChainDestination
- [x] 2.2 更新 `langchain/chains/__init__.py` — 导出 RouterChain, LLMRouterChain, ChainDestination

## 3. Sphinx 文档

- [x] 3.1 新增 `docs/notes/router-philosophy.rst` — Router 设计哲学（Dynamic Option Injection 模式，Router vs Agent 边界）
- [x] 3.2 新增 `docs/examples/router-example.rst` — MultiPrompt 示例 + 路由到 RetrievalChain 示例
- [x] 3.3 新增 `docs/api/router.rst` — RouterChain, LLMRouterChain, ChainDestination API 文档
- [x] 3.4 更新 `docs/api/index.rst`, `docs/examples/index.rst`, `docs/notes/index.rst` — 注册新文档页面