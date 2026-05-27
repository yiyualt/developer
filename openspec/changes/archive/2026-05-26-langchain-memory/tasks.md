## 1. Memory 模块

- [x] 1.1 实现 `langchain/memory/base.py`：Memory ABC（save_context, load_context, clear）
- [x] 1.2 实现 `langchain/memory/buffer.py`：ConversationBufferMemory（保存完整对话历史）
- [x] 1.3 实现 `langchain/memory/buffer_window.py`：ConversationBufferWindowMemory（只保留最近 K轮）
- [x] 1.4 创建 `langchain/memory/__init__.py` 并导出 Memory, ConversationBufferMemory, ConversationBufferWindowMemory

## 2. LLMChain 修改

- [x] 2.1 修改 `langchain/chains/llm_chain.py`：新增可选 `memory` 参数，run() 中自动 load/save

## 3. Agent 修改

- [x] 3.1 修改 `langchain/agents/agent.py`：新增可选 `memory` 参数，run() 中自动 load/save

## 4. 包导出更新

- [x] 4.1 更新 `langchain/__init__.py` 导出 Memory, ConversationBufferMemory, ConversationBufferWindowMemory

## 5. 文档更新

- [x] 5.1 创建 `docs/api/memory.rst`（Memory autodoc section）
- [x] 5.2 更新 `docs/api/index.rst` toctree 添加 memory
- [x] 5.3 创建 `docs/notes/memory-design.rst`
- [x] 5.4 更新 `docs/notes/index.rst` toctree 添加 memory-design
- [x] 5.5 创建 `docs/examples/memory-example.rst`
- [x] 5.6 更新 `docs/examples/index.rst` toctree 添加 memory-example

## 6. 构建验证

- [x] 6.1 全量构建 `sphinx-build`（删除 _build 后重建），确认成功，0 warnings
- [x] 6.2 验证 `from langchain import ConversationBufferMemory` 正常工作