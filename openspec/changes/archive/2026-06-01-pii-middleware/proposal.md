## Why

Middleware 系统已建立（v0.0.24）。PIIMiddleware 是第二个内置 Middleware——在工具输入进入执行前，自动检测和脱敏邮箱、信用卡号等个人信息。遵循官方 API 风格：`PIIMiddleware("email", strategy="redact")`。

## What Changes

- 新增 `PIIMiddleware(Middleware)`：在 `before_tool` 中用正则检测 PII，按策略替换
- 支持 `strategy`: `"redact"`（替换为 `[REDACTED]`）和 `"mask"`（保留部分字符）
- 支持 pii_type: `"email"`, `"credit_card"`

## Capabilities

### New Capabilities
- `pii-middleware`: PIIMiddleware 在工具执行前自动检测和脱敏工具输入中的敏感信息

### Modified Capabilities
(无)

## Impact

- 修改文件：`langchain/agents/middleware.py`
- 导出：已通过 Middleware ABC 导出，无需额外操作
