## Context

LangChain v0.0.1 已实现三个核心原语（PromptTemplate、LLM ABC、FakeLLM、LLMChain），但只有 FakeLLM 返回固定字符串。框架需要真实 LLM 才能让后续演进有意义。OpenAI API 是 LangChain 历史上第一个对接的 LLM provider。

当前 LLM ABC 的设计很简单：子类只需实现 `_generate(prompts: list[str]) -> list[str]`。OpenAI 的 Completions API 返回的是更复杂的结构（choices、usage 等），需要在 `_generate` 内部做映射。

## Goals / Non-Goals

**Goals:**
- 实现 `langchain.llms.openai.OpenAI` 类，继承 LLM ABC，调用 OpenAI Chat Completions API
- 支持模型选择（model_name）、生成参数（temperature、max_tokens）
- API key 通过环境变量 `OPENAI_API_KEY` 或构造参数传入
- 与 FakeLLM 统一接口：`generate(["prompt"])` 返回 `["response"]`
- 更新文档反映真实 LLM 的存在

**Non-Goals:**
- 不实现流式响应（streaming）——后续版本的内容
- 不实现异步调用——后续版本的内容
- 不实现 Chat Model 抽象（与 LLM 分离的 ChatML 接口）——v0.0.x 还没有这个分离
- 不实现 token 计数、成本追踪
- 不实现 retry / error handling 逻辑（先跑通最简路径）

## Decisions

### D1: 使用 OpenAI Chat Completions API 而非 Legacy Completions API

**选择**: `openai.chat.completions.create` (Chat Completions)
**理由**: OpenAI 已废弃 Legacy Completions API（`/v1/completions`）。Chat Completions 是当前和未来的标准接口。虽然 LangChain 原始 v0.0.1 用的是 Legacy API，但时间线还原不是盲从历史——我们还原的是设计理念，不是废弃的技术。
**替代**: Legacy Completions API（已被 OpenAI 官方标记为 deprecated）

### D2: 单 prompt 映射到单 message

**选择**: 每个 prompt 字符串映射为 Chat Completions 的一个 `user` message
**理由**: v0.0.x 时代 LangChain 的 LLM 接口是 string → string，没有 system prompt 或 conversation history。最简单的映射就是把 prompt 当作一条 user message。
**替代**: 支持 system prompt 参数（增加复杂度，v0.0.x 不需要）

### D3: API key 传入方式

**选择**: 环境变量 `OPENAI_API_KEY` 为默认，构造参数 `openai_api_key` 为备选
**理由**: 这是 LangChain 和 OpenAI SDK 的标准模式。环境变量最方便，构造参数用于需要多个 key 或非标准配置的场景。
**替代**: 只支持构造参数（不够便利）、配置文件（过度工程化）

### D4: openai SDK 版本

**选择**: 使用 `openai` Python SDK v1.x（最新版）
**理由**: v1.x 是当前稳定版，API 接口与 v0.x 完全不同。用最新版确保长期可用。
**替代**: v0.x（已废弃，不推荐）

## Risks / Trade-offs

- [OpenAI API 需要付费，测试成本不可忽略] → 优先用 gpt-4o-mini（最便宜的模型），开发时尽量用 FakeLLM，只在关键验证时切换真实 LLM
- [网络延迟和 API 不稳定性] → 暂不实现 retry，后续版本加入
- [API key 安全性] → 不在代码中硬编码 key，只通过环境变量或构造参数传入