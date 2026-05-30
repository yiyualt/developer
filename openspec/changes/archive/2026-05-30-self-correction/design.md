## Context

当前 Agent 输出是一次性的——ReAct 循环终止后，答案直接返回。没有验证步骤。如果输出格式错误、漏了关键信息、或逻辑不通，调用方只能坦然接受。

## Goals / Non-Goals

**Goals:**
- `SelfCorrectingAgent`：包装 Agent，添加 输出检验 → 不通过则重试 的循环
- `LLMCorrector`：用 LLM 检验输出质量，返回 `(passed, feedback)`
- 重试时 feedback 追加到原问题中

**Non-Goals:**
- 不在 ReAct 循环中间纠错（只校验 Final Answer）
- 不实现规则校验器（v1 只用 LLM 做校验）
- 不修改 Agent 类本身

## Decisions

### Decision 1: 包装模式而非继承

**选择**：`SelfCorrectingAgent` 是一个包装类，内部持有 Agent 实例。
**理由**：任意 Agent（ReAct、PlanAndExecute）都能被包装。组合优于继承。

### Decision 2: Corrector 接口

```python
class LLMCorrector:
    def check(self, question: str, answer: str) -> tuple[bool, str]:
        """Returns (passed, feedback)."""
```

最简单的 `check` 方法：向 LLM 提问 "这个答案是否合理？"，根据回复判断。

### Decision 3: 重试时 feedback 追加到 question

```python
# 第一次：原始问题
answer = agent.run("计算圆的面积")

# 如果第一次答案校验不通过：
answer = agent.run("计算圆的面积\n\n上次答案有这些问题：公式用错了。请修正。")
```

### Decision 4: max_retries 默认 3

防止无限循环。三次尝试后返回最后一次结果（无论是否通过）。

## Risks / Trade-offs

- **校验 LLM 也可能出错**：LLM 校验器不是绝对可靠的。→ 这是 v1 的已知限制。后续可加入规则校验器（JSON schema 校验等）。
- **额外 LLM 调用**：每次校验多调一次 LLM。→ 默认 3 次重试 = 最多额外 2 次校验调用。
