## Why

当前 LangChain 只有 FakeLLM，返回固定字符串，无法产生真实的 LLM 行为（不确定性、结构化失败、幻觉）。框架在假地基上运行，后续演进（OutputParser、SequentialChain）都失去意义。接入 OpenAI API 是让框架变成真实可用系统的第一步——这也与 LangChain 原始历史一致：v0.0.1 之后就对接了 OpenAI。

## What Changes

- 新增 `langchain.llms.openai.OpenAI`：基于 `openai` Python SDK 的真实 LLM 实现
- 新增依赖：`openai` Python SDK
- OpenAI LLM 支持 `generate` 方法（与 FakeLLM 统一接口）
- 支持通过 `model_name` 参数选择模型（gpt-4o-mini 等）
- 支持通过 `temperature`、`max_tokens` 等参数控制生成行为
- 更新 `langchain.llms.__init__.py` 导出 OpenAI
- 更新 `langchain/__init__.py` 导出 OpenAI
- 更新文档：API page、Tutorial 补充真实 LLM 使用说明、Note 解释 FakeLLM vs Real LLM

## Capabilities

### New Capabilities
- `openai-llm`: OpenAI API 的 LLM 实现，支持模型选择、生成参数配置、统一 LLM 接口

### Modified Capabilities
- `llm-interface`: LLM base class 需要支持构造参数传递（temperature 等），从纯 ABC 扩展为可配置基类
- `doc-content-structure`: Tutorial 和 Notes 页面需要补充真实 LLM 相关内容

## Impact

- 新增 Python 依赖：`openai`
- `langchain/llms/openai.py` — 新文件
- `langchain/llms/base.py` — 可能需要小幅调整以支持通用构造参数
- `langchain/llms/__init__.py` — 新导出
- `langchain/__init__.py` — 新导出
- `docs/api/llms.rst` — 新增 OpenAI section
- `docs/tutorials/getting-started.rst` — 补充真实 LLM 用法
- `docs/notes/chain-design-philosophy.rst` — 补充 FakeLLM vs Real LLM 讨论