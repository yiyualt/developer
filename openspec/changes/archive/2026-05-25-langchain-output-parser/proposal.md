## Why

LLMChain 返回原始字符串，但实际应用需要结构化数据——JSON 对象、列表、枚举值等。没有 OutputParser，链的输出只能被人类阅读，无法被程序处理。这是 v0.0.1 之后最紧迫的扩展：有了真实 LLM，才能观察到自由文本输出的不可预测性，从而理解为什么需要解析器来把"近似结构化"的文本变成真正的数据结构。

## What Changes

- 新增 `langchain.output_parsers.OutputParser`：抽象基类，定义 `parse(text: str)` 接口
- 新增 `langchain.output_parsers.JsonOutputParser`：将 LLM 输出解析为 JSON dict
- 新增 `langchain.output_parsers.ListOutputParser`：将 LLM 输出解析为逗号分隔列表
- 修改 `LLMChain`：新增可选 `output_parser` 参数，`run()` 返回解析后的数据而非原始字符串
- 更新包导出
- 更新文档：API page、Tutorial 补充 parser 用法、Notes 新增 output-parsing-philosophy

## Capabilities

### New Capabilities
- `output-parser`: OutputParser 抽象基类 + JsonOutputParser + ListOutputParser，将 LLM 自由文本输出解析为结构化数据

### Modified Capabilities
- `llm-chain`: LLMChain 新增可选 `output_parser` 参数，run/apply 返回值随 parser 存在而变化
- `doc-content-structure`: Tutorial 和 Notes 页面补充 parser 相关内容

## Impact

- `langchain/output_parsers/` — 新模块
- `langchain/chains/llm_chain.py` — 修改（新增 output_parser 参数）
- `langchain/__init__.py` — 新导出
- `docs/` — 多个页面更新