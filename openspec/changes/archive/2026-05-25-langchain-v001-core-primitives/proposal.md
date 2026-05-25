## Why

LangChain v0.0.1 (Oct 2022) 的起点极其简单：三个核心原语 PromptTemplate、LLM、LLMChain，回答了一个根本问题——"如何把提示词和大模型串联起来完成一个任务？" 这是整个框架的基因，所有后续演化（Agent、Memory、LCEL）都从这里长出来。

## What Changes

- 新增 `langchain.prompts.PromptTemplate`：将变量填入模板文本，生成完整提示词
- 新增 `langchain.llms.LLM`：大模型调用的统一抽象基类
- 新增 `langchain.llms.FakeLLM`：用于测试的模拟 LLM 实现
- 新增 `langchain.chains.LLMChain`：将 PromptTemplate + LLM 串联执行的核心链
- 更新 `langchain/__init__.py`：导出上述三个模块的顶层类
- 新增 doc 内容：Tutorial（getting-started）、Notes（chain-design-philosophy）、Example（simple-qa）、API pages

## Capabilities

### New Capabilities
- `prompt-template`: 提示词模板系统，支持变量替换和模板验证
- `llm-interface`: 大模型调用抽象接口，包含基类和模拟实现
- `llm-chain`: 将 PromptTemplate 与 LLM 串联执行的核心链原语

### Modified Capabilities
- `doc-content-structure`: 从占位状态更新为包含 v0.0.1 的实际内容（tutorial、note、example）

## Impact

- `langchain/prompts/` — 新模块
- `langchain/llms/` — 新模块
- `langchain/chains/` — 新模块
- `langchain/__init__.py` — 新的导出
- `docs/tutorials/` — 新增 getting-started 页面
- `docs/notes/` — 新增 chain-design-philosophy 页面
- `docs/examples/` — 新增 simple-qa 页面
- `docs/api/` — 新增 prompts.rst、llms.rst、chains.rst