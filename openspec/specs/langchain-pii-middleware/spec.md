## ADDED Requirements

### Requirement: PIIMiddleware redacts sensitive data from tool input
PIIMiddleware SHALL extend Middleware and intercept `before_tool` to detect and redact PII from tool inputs. Supported types SHALL be "email" and "credit_card". Strategy "redact" SHALL replace matches with `[REDACTED]`. Strategy "mask" SHALL preserve the last 4 characters and replace earlier characters with `*`.

#### Scenario: Email redaction
- **WHEN** PIIMiddleware("email", strategy="redact").before_tool("send_email", "Send to alice@example.com")
- **THEN** the returned input SHALL be "Send to [REDACTED]"

#### Scenario: Email masking
- **WHEN** PIIMiddleware("email", strategy="mask").before_tool("send_email", "Send to alice@example.com")
- **THEN** the email SHALL be masked, preserving the last 4 characters before the @ and the domain

#### Scenario: No PII found — pass through
- **WHEN** PIIMiddleware("email").before_tool("calc", "2+3")
- **THEN** the input SHALL be "2+3" unchanged
