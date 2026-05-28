## Why

经过 9 个版本的演进，LangChain 已经有了 Chain 嵌套、Agent 多步推理、Memory 自动管理等复杂执行流程。但这些执行过程对开发者完全不可见——LLM 调了几次、花了多少 token、哪步出错、Agent 的 Thought 流实时输出——全部是黑盒。真实 LangChain 在 2023 年初遇到同样问题后引入了 Callback 系统，让执行过程变得可观测、可调试、可追踪。

## What Changes

- 新增 CallbackHandler ABC — 定义生命周期钩子（on_llm_start/end, on_chain_start/end, on_tool_start/end, on_agent_action/finish, on_error）
- LLMChain、SequentialChain、Agent、Tool 等组件在执行关键节点触发 callbacks
- 新增 StdOutCallbackHandler — 内置实现，打印执行日志到终端
- 组件接受 `callbacks` 参数，注册回调处理器列表

## Capabilities

### New Capabilities
- `callback`: CallbackHandler ABC 及内置 StdOutCallbackHandler，定义组件执行生命周期事件钩子

### Modified Capabilities
- `llm-chain`: LLMChain 接受 callbacks 参数，在 run() 关键节点触发 on_chain_start/end 和 on_llm_start/end
- `agent`: Agent 在 ReAct 循环中触发 on_agent_action/finish 和 on_tool_start/end
- `tool`: Tool 在 run() 时触发 on_tool_start/end

## Impact

- 新模块 `langchain/callbacks/`（base.py, stdout.py）
- 修改 LLMChain、Agent、Tool 的 __init__ 和 run() 方法，增加 callbacks 参数和触发点
- 不改变现有 API 的返回值，回调是纯附加行为
- 更新 `langchain/__init__.py` 导出 CallbackHandler 和 StdOutCallbackHandler
- Sphinx 文档：新增 callback-philosophy.rst、callback-example.rst、api/callback.rst