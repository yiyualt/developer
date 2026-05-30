## Why

Agent 输出可能格式错误、逻辑矛盾、或不符合预期。当前 Agent 没有自我检查和修正机制——输出了一个错误答案就结束了。Self-Correction 让 Agent 能审视自己的输出，发现问题后自动重试。这是"质量保障"方向的第一步：从"产出答案"到"产出可靠答案"。

## What Changes

- 新增 `SelfCorrectingAgent`：包装任意 Agent，输出后自动检查，不通过则重试（最多 N 次）
- 新增 `LLMCorrector`：用 LLM 检查输出质量，返回 (通过/未通过, 反馈信息)
- 重试时将反馈信息追加到 Agent 的问题中，让 Agent 知道上次哪里不对

## Capabilities

### New Capabilities
- `self-correction`: Agent 输出的自动检查与修正——输出后由 Corrector 验证，不合格则带着反馈重试

### Modified Capabilities
(无 — 纯增量)

## Impact

- 新增文件：`langchain/agents/self_correct.py`（SelfCorrectingAgent + LLMCorrector）
- 修改文件：`langchain/agents/__init__.py`、`langchain/__init__.py`
- 无破坏性变更
