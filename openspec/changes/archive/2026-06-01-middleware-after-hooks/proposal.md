## Why

当前 Middleware ABC 只有 `before_tool` 和 `before_llm`——都是变换输入。缺少 after 钩子（变换输出），导致 Model Fallback、Model Retry、Tool Retry 等官方 Middleware 无法实现。补全 `after_llm` 和 `after_tool`，解锁 Runtime 系列的全部功能。

## What Changes

- Middleware ABC 新增 `after_llm(messages, response) -> response`：LLM 调用后变换或替换响应
- Middleware ABC 新增 `after_tool(tool_name, tool_input, result) -> result`：工具调用后变换或替换结果
- Agent._react_loop 中 LLM 调用后遍历 middleware.after_llm
- Agent._execute_tool 中工具调用后遍历 middleware.after_tool

## Capabilities

### New Capabilities
- `middleware-after-hooks`: Middleware ABC 的 after_llm + after_tool 钩子

### Modified Capabilities
- `middleware-system`: Middleware ABC 新增两个钩子
- `agent`: Agent 循环调用 after_llm / after_tool

## Impact

- 修改：`langchain/agents/middleware.py`（ABC 新增 2 个方法）、`langchain/agents/agent.py`（2 处调用点）
- 无破坏性变更（默认透传）
