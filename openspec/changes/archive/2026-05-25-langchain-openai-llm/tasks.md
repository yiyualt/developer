## 1. 安装依赖

- [x] 1.1 安装 `openai` Python SDK，更新 `pyproject.toml` 添加依赖

## 2. OpenAI LLM 实现

- [x] 2.1 实现 `langchain/llms/openai.py`：OpenAI 类（继承 LLM，调用 Chat Completions API）
- [x] 2.2 支持 `model_name`（默认 gpt-4o-mini）、`temperature`、`max_tokens` 参数
- [x] 2.3 支持 API key 通过 `openai_api_key` 构造参数或 `OPENAI_API_KEY` 环境变量传入
- [x] 2.4 实现 `_generate` 方法：每个 prompt 作为一条 user message 调用 Chat Completions
- [x] 2.5 为 OpenAI 类编写 docstring

## 3. LLM 基类微调

- [x] 3.1 修改 `langchain/llms/base.py`：添加 `model_name` 和 `temperature` 可选构造参数存储为实例属性 — 跳过，OpenAI 在自己的 __init__ 中直接处理，ABC 保持最小接口

## 4. 包导出更新

- [x] 4.1 更新 `langchain/llms/__init__.py` 导出 OpenAI
- [x] 4.2 更新 `langchain/__init__.py` 导出 OpenAI

## 5. 文档更新

- [x] 5.1 更新 `docs/api/llms.rst` 添加 OpenAI autodoc section
- [x] 5.2 更新 `docs/tutorials/getting-started.rst` 补充真实 OpenAI LLM 使用段落
- [x] 5.3 更新 `docs/notes/chain-design-philosophy.rst` 补充 FakeLLM vs Real LLM 讨论

## 6. 构建验证

- [x] 6.1 运行 `make html`，确认构建成功
- [x] 6.2 验证 `import langchain; from langchain.llms import OpenAI` 正常工作