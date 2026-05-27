## Why

当前所有 Chain 都是固定执行路径 — SequentialChain 是 A→B→C，RetrievalChain 是 embed→search→gen。
无法根据输入内容动态选择不同的处理方式。Router Chain 引入条件分支能力，
让 LLM 根据问题意图自动路由到最合适的 Chain（LLMChain、RetrievalChain、Agent 等），
这是 LangChain 从"线性管道"走向"动态编排"的关键一步。

## What Changes

- 新增 **RouterChain ABC** — 定义路由接口 `route()` 方法
- 新增 **LLMRouterChain** — 用 LLM + JsonOutputParser 做路由决策
- 新增 **ChainDestination** — 描述一个目标 Chain（name + description + chain 实例）
- RouterChain 支持路由到任意 Chain 类型（LLMChain、RetrievalChain、Agent）
- RouterChain 必须指定 default destination 作为 fallback

## Capabilities

### New Capabilities
- `router-chain`: 动态路由决策，根据输入选择不同的 Chain 执行

### Modified Capabilities
(无 — RouterChain 是独立的新组件，不修改已有 Chain 的行为)

## Impact

- 新增 Python 模块: `langchain/chains/router.py`
- 更新 `langchain/__init__.py` — 导出 RouterChain, LLMRouterChain, ChainDestination
- 更新 `langchain/chains/__init__.py` — 导出新组件
- 无新外部依赖
- 新增 Sphinx 文档