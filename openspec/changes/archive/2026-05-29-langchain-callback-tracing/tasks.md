## 1. CallbackHandler ABC

- [x] 1.1 创建 `langchain/callbacks/base.py` — CallbackHandler ABC，定义 9 个空钩子方法（on_llm_start/end, on_chain_start/end, on_tool_start/end, on_agent_action/finish, on_error），每个方法接受 **kwargs
- [x] 1.2 创建 `langchain/callbacks/__init__.py`
- [x] 2.1 创建 `langchain/callbacks/stdout.py` — StdOutCallbackHandler，每个钩子打印 `[ComponentType] Event: detail` 格式的日志到 stdout

## 3. 组件集成 Callbacks

- [x] 3.1 更新 `langchain/chains/llm_chain.py` — LLMChain 接受 callbacks 参数，run() 中触发 on_chain_start/end、on_llm_start/end、on_error
- [x] 3.2 更新 `langchain/agents/agent.py` — Agent 接受 callbacks 参数，_run_loop() 中触发 on_agent_action/finish、on_tool_start/end、on_error
- [x] 3.3 更新 `langchain/tools/base.py` — Tool 接受 callbacks 参数，run() 中触发 on_tool_start/end、on_error

## 4. 整合与导出

- [x] 4.1 更新 `langchain/__init__.py` — 导出 CallbackHandler 和 StdOutCallbackHandler

## 5. Sphinx 文档

- [x] 5.1 创建 `docs/notes/callback-philosophy.rst` — Callback 设计哲学：为什么用 Handler 模式、事件粒度选择、与真实 LC 的演进对比
- [x] 5.2 创建 `docs/examples/callback-example.rst` — StdOutCallbackHandler 使用示例，展示 LLMChain 和 Agent 的回调输出
- [x] 5.3 创建 `docs/api/callbacks.rst` — CallbackHandler 和 StdOutCallbackHandler 的 autoclass
- [x] 5.4 更新 `docs/api/index.rst` — 增加 callbacks 条目
- [x] 5.5 更新 `docs/notes/index.rst` — 增加 callback-philosophy 条目
- [x] 5.6 更新 `docs/examples/index.rst` — 增加 callback-example 条目