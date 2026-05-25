## Why

LLMChain 只能做一步。但真实任务往往需要多步推理——先提取主题，再根据主题生成详细描述，最后把描述翻译成另一种语言。SequentialChain 把多个 LLMChain 串联起来，每一步的输出作为下一步的输入。有了 OutputParser，第一步的结构化输出可以精确传入第二步，而不是传递混乱的原始字符串。

## What Changes

- 新增 `langchain.chains.SequentialChain`：将多个 LLMChain 按顺序串联执行
- SequentialChain 支持 `input_variables` 和 `output_variables` 声明
- 每一步 chain 的输出 key 映射到下一步 chain 的输入 key
- 更新包导出
- 更新文档：API page、Notes 新增 sequential-chain-design、Examples 新增 multi-step

## Capabilities

### New Capabilities
- `sequential-chain`: 多步链式执行，将多个 LLMChain 串联，每步输出传递到下步输入

### Modified Capabilities
- `llm-chain`: LLMChain 需要声明 `output_keys`（默认为 `["text"]`），以便 SequentialChain 知道每步产出什么
- `doc-content-structure`: Notes 和 Examples 页面补充 SequentialChain 相关内容

## Impact

- `langchain/chains/sequential.py` — 新文件
- `langchain/chains/llm_chain.py` — 小幅修改（新增 output_keys 属性）
- `langchain/chains/__init__.py` — 新导出
- `langchain/__init__.py` — 新导出
- `docs/` — 多个页面更新