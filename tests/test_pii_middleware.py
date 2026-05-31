"""Tests for PIIMiddleware — redaction and masking of sensitive data."""

from langchain.agents.middleware import PIIMiddleware


def test_email_redact():
    mw = PIIMiddleware("email", strategy="redact")
    _, result = mw.before_tool("send_email", "Send to alice@example.com")
    assert "alice@example.com" not in result
    assert "[REDACTED]" in result


def test_email_mask():
    mw = PIIMiddleware("email", strategy="mask")
    _, result = mw.before_tool("send_email", "Send to alice@example.com")
    assert "alice@example.com" not in result
    # Mask preserves the last chars of the local part and the domain
    assert "@" not in result or "****" in result


def test_credit_card_redact():
    mw = PIIMiddleware("credit_card", strategy="redact")
    _, result = mw.before_tool("payment", "Card: 4111-1111-1111-1111")
    assert "4111" not in result
    assert "[REDACTED]" in result


def test_credit_card_mask():
    mw = PIIMiddleware("credit_card", strategy="mask")
    _, result = mw.before_tool("payment", "Card: 4111-1111-1111-1111")
    # Last 4 digits preserved
    assert "1111" in result


def test_no_pii_pass_through():
    mw = PIIMiddleware("email")
    _, result = mw.before_tool("calc", "2+3")
    assert result == "2+3"


def test_multiple_emails():
    mw = PIIMiddleware("email", strategy="redact")
    _, result = mw.before_tool("send", "To: a@b.com and c@d.com")
    assert result.count("[REDACTED]") == 2


def test_unknown_pii_type():
    try:
        PIIMiddleware("phone")
        assert False, "should raise"
    except ValueError as e:
        assert "phone" in str(e)


def test_unknown_strategy():
    try:
        PIIMiddleware("email", strategy="delete")
        assert False, "should raise"
    except ValueError as e:
        assert "delete" in str(e)


if __name__ == "__main__":
    import sys
    fns = [n for n in dir() if n.startswith("test_")]
    p = f = 0
    for fn in sorted(fns):
        try:
            globals()[fn]()
            print(f"  ✓ {fn}")
            p += 1
        except Exception as e:
            print(f"  ✗ {fn}: {e}")
            f += 1
    print(f"\n{p} passed, {f} failed")
    sys.exit(1 if f else 0)
