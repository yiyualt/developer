## Context

LLMChain.apply_async() 已建立模式：用 asyncio.gather 并发调用 LLM.agenerate()。Agent 层只需要同样的模式——多个问题并发，每个问题在独立的 ReAct 循环中用 agenerate()。

## Goals / Non-Goals

**Goals:**
- `Agent.apply_async(questions)` — 并发运行多个问题
- 内部每步用 `llm.agenerate()` 替代同步 `generate()`
- 与 `LLMChain.apply_async()` API 对称

**Non-Goals:**
- 不加 `Agent.arun()` — 单次 async 调用只需 `agent.run()` 或 `apply_async([q])[0]`
- 不加 `Agent.astream()` — 流式不需要 async 版本
- 不修改 Memory、Tool、PlanAndExecute 的 async 支持

## Decisions

### Decision 1: 只加 apply_async，不加 arun

**选择**：`apply_async(questions) -> list[str]`，无 `arun(question) -> str`。

**理由**：v0.0.12 哲学——async 的价值在并发。单个 `arun()` 等同于 `apply_async([question])[0]`。LLMChain 也只有 `apply_async`，没有 `arun`。保持一致。

### Decision 2: _arun_loop — 异步 ReAct 循环

```python
async def _arun_loop(self, question: str) -> str:
    # 与 _run_loop 相同逻辑，但 llm.generate → await llm.agenerate
    # Memory、callbacks 等保持同步
```

只改 LLM 调用那一行：`generate` → `agenerate`。Memory、callbacks、tool execution 保持同步。

### Decision 3: apply_async 实现

```python
async def apply_async(self, questions: List[str]) -> List[str]:
    async def _run_one(question):
        result = await self._arun_loop(question)
        return result["answer"]
    return await asyncio.gather(*[_run_one(q) for q in questions])
```

每个 Agent 实例被复用——`_arun_loop` 在同一个 Agent 实例上运行，但每个协程有独立的 scratchpad 和迭代状态。
