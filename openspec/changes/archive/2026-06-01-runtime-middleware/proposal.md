## Why

当前 Agent 没有调用次数限制——LLM 可能无限循环，工具可能被反复调用。Runtime Middleware 添加限速能力：ModelCallLimitMiddleware（限制 LLM 调用次数）和 ToolCallLimitMiddleware（限制工具调用次数）。两个都实现为 Middleware 子类，透明地插入 Agent 循环。

## What Changes

- 新增 `ModelCallLimitMiddleware(Middleware)`：在 `before_llm` 中计数，超出 `max_calls` 时返回空消息阻止 LLM 调用
- 新增 `ToolCallLimitMiddleware(Middleware)`：在 `before_tool` 中计数，超出 `max_calls`（或 `per_tool` 限制）时返回 `(False, "Limit exceeded")`
- 支持 `per_tool` 配置：`ToolCallLimitMiddleware(max_calls={"calculator": 3, "search": 5})`

## Capabilities

### New Capabilities
- `runtime-middleware`: ModelCallLimitMiddleware + ToolCallLimitMiddleware，提供 LLM 和工具调用的速率限制

### Modified Capabilities
(无 — 纯新增 Middleware)

## Impact

- 修改：`langchain/agents/middleware.py`
- 导出：两个新类
- 无破坏性变更
