## Context

Pyleaf/developer 项目已建立 Sphinx 文档系统和 `langchain` 包根模块（v0.0.1），但包内只有空的 `__init__.py`。现在要实现 LangChain v0.0.1 的三个核心原语——这是框架的起点，也是整个演化叙事的第一章。

LangChain 原始 v0.0.1（2022 年 10 月）的设计极其克制：只解决"如何把提示词和大模型串联起来"这一个问题。没有 Agent、没有 Memory、没有 Retriever，就是 Prompt + LLM = Chain。

## Goals / Non-Goals

**Goals:**
- 实现 PromptTemplate、LLM 基类、FakeLLM、LLMChain 四个核心类
- 每个 class 的接口和语义与 LangChain v0.0.1 一致
- 为每个模块编写 docstring（支持 autodoc）
- 在 docs 四层结构中填入 v0.0.1 的实际内容
- 所有代码可测试（FakeLLM 不依赖外部 API）

**Non-Goals:**
- 不对接真实 LLM API（OpenAI 等）——v0.0.1 只需要 FakeLLM
- 不实现 Agent、Memory、Tool——这些是后续版本的内容
- 不实现异步或流式调用
- 不考虑序列化/持久化

## Decisions

### D1: PromptTemplate 使用 Python f-string 风格的变量语法

**选择**: `"{variable_name}"` 作为模板变量标记
**理由**: 这与 LangChain 原始 v0.0.1 一致，也是 Python 社区最直觉的方式。Jinja2 更强大但 v0.0.1 时代还没有这个需求。
**替代**: Jinja2 模板（过于复杂，不适合 v0.0.1 的极简定位）

### D2: LLM 基类设计为 ABC

**选择**: `LLM` 作为抽象基类，子类 MUST 实现 `_generate` 方法
**理由**: LangChain v0.0.1 的 LLM 是所有模型调用的统一接口。ABC 强制子类实现核心方法，同时提供 `generate` / `call` 等公共入口。这与原始设计一致。
**替代**: Protocol（更轻量但 v0.0.1 时代 Python typing 还不够成熟）

### D3: LLMChain 的执行模型

**选择**: `LLMChain.run(inputs) → str` 和 `LLMChain.apply(inputs) → list[str]`
**理由**: `run` 是最简单的单输入单输出，`apply` 支持批量。这直接反映了 v0.0.1 的"chain = prompt + llm"语义。
**替代**: 返回复杂对象（v0.0.1 没有 OutputParser，就是返回原始字符串）

### D4: FakeLLM 的实现策略

**选择**: FakeLLM 直接返回固定字符串或根据输入返回模板化内容
**理由**: 测试不需要真实 API 调用。FakeLLM 让所有测试离线可运行。这也是 LangChain 原始设计中就有的模式。
**替代**: Mock 对象（不够真实，无法验证 chain 的完整执行路径）

### D5: 模块目录结构

**选择**:
```
langchain/
├── __init__.py         ← 导出 PromptTemplate, LLM, LLMChain
├── prompts/
│   ├── __init__.py
│   └── prompt.py       ← PromptTemplate
├── llms/
│   ├── __init__.py
│   ├── base.py         ← LLM ABC
│   └── fake.py         ← FakeLLM
├── chains/
│   ├── __init__.py
│   └── llm_chain.py    ← LLMChain
```

**理由**: 每个核心概念有自己的 namespace，与 LangChain 原始结构和 PyTorch 的模块化风格一致。
**替代**: 所有类放在根目录（不利于后续版本扩展）

## Risks / Trade-offs

- [PromptTemplate 不支持 Jinja2，未来迁移可能需要 BREAKING 改动] → v0.2.0 引入 LCEL 时自然会处理，这是时间线还原的一部分
- [LLM ABC 过于简单，缺少 streaming / async 支持] → 有意为之，这些能力在后续版本才出现
- [FakeLLM 太简陋，无法测试边界情况] → 后续版本会增加更多测试工具