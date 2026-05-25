## 1. SequentialChain 实现

- [x] 1.1 实现 `langchain/chains/sequential.py`：SequentialChain 类（chains 列表、input_variables、run 方法）
- [x] 1.2 实现数据流机制：每步 chain 的 output dict 合入下一步的 input dict
- [x] 1.3 实现 input 验证：检查所有 input_variables 和每步所需变量是否被满足
- [x] 1.4 为 SequentialChain 编写 docstring

## 2. LLMChain 修改

- [x] 2.1 修改 `langchain/chains/llm_chain.py`：新增 `output_keys` 属性（默认 ["text"]）
- [x] 2.2 新增 `_call_internal()` 方法：返回 dict 格式的 output（用于 SequentialChain 内部调用），与 `run()` 返回裸值的行为区分

## 3. 包导出更新

- [x] 3.1 更新 `langchain/chains/__init__.py` 导出 SequentialChain
- [x] 3.2 更新 `langchain/__init__.py` 导出 SequentialChain

## 4. 文档更新

- [x] 4.1 创建 `docs/api/chains.rst` 补充 SequentialChain autodoc section（如已有 chains.rst 则更新）
- [x] 4.2 创建 `docs/notes/sequential-chain-design.rst`
- [x] 4.3 更新 `docs/notes/index.rst` toctree 添加 sequential-chain-design
- [x] 4.4 创建 `docs/examples/multi-step.rst`
- [x] 4.5 更新 `docs/examples/index.rst` toctree 添加 multi-step

## 5. 构建验证

- [x] 5.1 运行 `make html`，确认构建成功
- [x] 5.2 验证 `from langchain.chains import SequentialChain` 正常工作