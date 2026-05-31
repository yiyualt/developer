## Context

当前 Middleware ABC 只有 `before_tool`——拦截工具执行。Summarization 需要另一种钩子：在 LLM 调用前变换消息列表。新增 `before_llm` 钩子补全 Middleware 的能力。

## Design

### Middleware ABC 新增 before_llm

```python
class Middleware(ABC):
    def before_llm(self, messages: list) -> list:
        """Called before each LLM call. Return transformed messages."""
        return messages
```

### Agent 调用 before_llm

在 `_react_loop` 中，构建消息后、调 LLM 前：

```python
for mw in self.middleware:
    call_messages = mw.before_llm(call_messages)
response = llm.generate([prompt])[0]  # 用变换后的消息
```

### SummarizationMiddleware

```python
class SummarizationMiddleware(Middleware):
    def __init__(self, llm, max_tokens=4000, keep_recent=3):
        self._llm = llm
        self.max_tokens = max_tokens
        self.keep_recent = keep_recent  # keep last N messages untouched

    def before_llm(self, messages):
        total_chars = sum(len(m.content) for m in messages)
        if total_chars < self.max_tokens * 4:  # ~4 chars per token
            return messages

        # Compress: summarize older messages, keep recent ones
        split = len(messages) - self.keep_recent
        older = messages[:split]
        recent = messages[split:]

        combined = "\n".join(f"[{m.role}]: {m.content}" for m in older)
        summary = self._summarize(combined)

        return [HumanMessage(f"Previous conversation summary:\n{summary}")] + recent

    def _summarize(self, text):
        prompt = f"Summarize concisely:\n{text}"
        return self._llm.generate([prompt])[0]
```

### 阈值策略

`max_tokens * 4` 是字符数近似（英文 ~4 chars/token）。压缩时保留最近 `keep_recent` 条消息不动，只摘要更早的部分。
