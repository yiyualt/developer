## 1. ConversationSummaryMemory 实现

- [x] 1.1 创建 `langchain/memory/summary.py` — ConversationSummaryMemory (llm 参数, _summary, _buffer, save_context, load_context, clear)
- [x] 1.2 实现摘要生成 — 用 LLMChain + 专用 prompt 压缩历史
- [x] 1.3 实现增量摘要 — 已有摘要时，不从头压缩，而是追加更新

## 2. Agent 中间步骤存入 Memory

- [x] 2.1 更新 `langchain/agents/agent.py` — `_run_loop` 结束时保存完整推理过程（Thought/Action/Observation/Final Answer），不只保存 Final Answer

## 3. 整合与导出

- [x] 3.1 更新 `langchain/memory/__init__.py` — 导出 ConversationSummaryMemory
- [x] 3.2 更新 `langchain/__init__.py` — 导出 ConversationSummaryMemory

## 4. Sphinx 文档

- [x] 4.1 更新 `docs/notes/memory-design.rst` — 补充 SummaryMemory vs Buffer vs Window 的对比
- [x] 4.2 更新 `docs/examples/memory-example.rst` — 新增 SummaryMemory 使用示例
- [x] 4.3 更新 `docs/api/memory.rst` — 新增 ConversationSummaryMemory 的 autoclass