## Context

LangChain 现有 PromptTemplate + LLM + LLMChain + OutputParser。LLMChain 做一步，OutputParser 解析一步的输出。但多步推理需要把多个 chain 串起来：step 1 的输出 → step 2 的输入 → step 3 的输入。

关键设计问题：step 1 的输出如何映射到 step 2 的输入？如果 step 1 用 OutputParser 返回 dict {"topic": "Python"}，step 2 的 PromptTemplate 需要 "{topic}"——需要一种 key 映射机制。

## Goals / Non-Goals

**Goals:**
- 实现 SequentialChain：按顺序串联多个 LLMChain
- 每步 chain 声明 output_keys（它产出什么变量）
- SequentialChain 自动将上一步的 output 映射到下一步的 input
- LLMChain 新增 output_keys 属性（默认 ["text"]）

**Non-Goals:**
- 不实现并行链（RouterChain / BranchingChain）
- 不实现条件分支（if/else 路径）
- 不实现循环（Agent 的 while loop 是后续版本）
- 不实现中间步骤的记忆共享

## Decisions

### D1: Key-based 数据流

**选择**: 每步 chain 声明 `output_keys`（如 `["topic", "summary"]`），SequentialChain 将上一步的 output dict 合入下一步的 input dict
**理由**: 最简单、最显式的数据流方式。每步 chain 的输出是一个 dict，key 名与下一步 PromptTemplate 的变量名对应时自动传入。如果 key 名不匹配，用户需要显式映射。
**替代**: 纯字符串传递（不利用 OutputParser 的结构化输出，浪费了 parser）

### D2: LLMChain.run() 和 apply() 的 output_keys 行为

**选择**: 当 output_parser 存在且返回 dict 时，output_keys 从 dict 的 keys 推断；当没有 parser 时，output_keys 默认为 ["text"]，run() 的结果被包装为 {"text": result}
**理由**: SequentialChain 需要每步产出 dict（key → value），不是裸值。run() 方便单步使用返回裸值，但 SequentialChain 内部需要 dict 格式。
**替代**: 强制 run() 总是返回 dict（破坏 v0.0.1 的简洁性）

### D3: SequentialChain 的执行模型

**选择**: `SequentialChain.run(**kwargs) -> dict` 始终返回最终 output dict（包含所有步骤的输出 key）
**理由**: 用户可能需要中间步骤的结果，不只是最终输出。返回完整 dict 让用户可以选择取哪个 key。
**替代**: 只返回最后一步的输出（丢失中间信息）

## Risks / Trade-offs

- [Key 名不匹配时数据流断裂] → 当前方案要求 key 名一致或手动映射，后续版本可加 key_mappings 参数
- [大 dict 在多步链中累积可能冗余] → 当前方案保留所有 key，后续版本可加 output_filter