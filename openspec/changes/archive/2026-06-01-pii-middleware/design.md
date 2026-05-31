## Context

Middleware.before_tool 接收原始工具输入。PIIMiddleware 在输入传给工具前，用正则检测敏感信息并脱敏。

## Design

```python
class PIIMiddleware(Middleware):
    PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    }

    def __init__(self, pii_type, strategy="redact"):
        self.pii_type = pii_type
        self.strategy = strategy
        self._pattern = re.compile(self.PATTERNS[pii_type])

    def before_tool(self, tool_name, tool_input):
        if self.strategy == "redact":
            cleaned = self._pattern.sub("[REDACTED]", tool_input)
        elif self.strategy == "mask":
            cleaned = self._pattern.sub(self._mask, tool_input)
        return (True, cleaned)

    def _mask(self, match):
        text = match.group()
        if len(text) > 4:
            return "*" * (len(text) - 4) + text[-4:]
        return "****"
```

- `strategy="redact"`: `alice@example.com` → `[REDACTED]`
- `strategy="mask"`: `alice@example.com` → `*********e.com`, credit card `1234-5678-9012-3456` → `************3456`
