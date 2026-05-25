## Context

LangChain v0.0.1 有 PromptTemplate + LLM + LLMChain，且已接入 DashScope/glm-5.1 真实 LLM。LLMChain.run() 返回原始字符串，这是 v0.0.1 最明显的限制——真实 LLM 的输出是自由文本，无法直接作为程序数据使用。OutputParser 把"近似结构化"的文本变成真正的 Python 数据结构。

## Goals / Non-Goals

**Goals:**
- 实现 OutputParser ABC，定义 parse(text) -> Any 接口
- 实现 JsonOutputParser：从 LLM 输出中提取 JSON dict
- 实现 ListOutputParser：从 LLM 输出中提取逗号分隔列表
- 修改 LLMChain 支持可选 output_parser，run() 返回解析结果
- 每个 class 有 docstring（支持 autodoc）

**Non-Goals:**
- 不实现 PydanticOutputParser（v0.0.x 时代还没有 Pydantic 验证需求）
- 不实现自动 prompt 格式化（告诉 LLM "请返回 JSON" 的指令）——这是后续版本的 OutputParser.get_format_instructions()
- 不实现错误恢复/重试（解析失败就抛异常，后续版本加 retry）

## Decisions

### D1: JsonOutputParser 提取策略

**选择**: 正则匹配 JSON 块（```json ... ``` 或 `{...}`），然后 json.loads 解析
**理由**: 真实 LLM 经常把 JSON 包在 markdown code block 里，或混入额外文本。直接 json.loads 整个字符串会失败，需要先提取 JSON 部分。
**替代**: 直接 json.loads（太脆弱，LLM 输出常有额外文本）

### D2: LLMChain 的 output_parser 行为

**选择**: 可选参数，不传 parser 时行为与 v0.0.1 一致（返回原始字符串）；传了 parser 时返回解析后的数据
**理由**: 向后兼容。v0.0.1 用户不需要改任何代码就能继续用。需要 parser 的人只需加一个参数。
**替代**: 强制所有链都传 parser（破坏 v0.0.1 兼容性）

### D3: apply() 的 parser 行为

**选择**: apply() 也支持 parser，返回 list[Any] 而非 list[str]
**理由**: 批量场景更需要结构化数据。一致性要求 run 和 apply 对 parser 的处理方式相同。
**替代**: apply 不支持 parser（不一致，会让用户困惑）

### D4: 模块目录结构

**选择**: `langchain/output_parsers/` 作为独立模块
**理由**: 与 prompts / llms / chains 同级的模块化风格一致。Parser 是独立概念，不是 chain 的附属。
**替代**: 把 parser 放在 chains/ 下（parser 不是 chain，放错位置）

## Risks / Trade-offs

- [JsonOutputParser 可能提取失败，LLM 输出格式不可控] → 当前方案是抛出异常，后续版本加 retry 和 get_format_instructions 来引导 LLM 输出正确格式
- [ListOutputParser 只支持逗号分隔，覆盖面窄] → v0.0.x 的极简定位，后续可扩展编号列表、换行列表等