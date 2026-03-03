from __future__ import annotations

import logging

from app.interfaces.api.middleware.redaction import RedactingFormatter


def test_redacting_formatter_masks_email_and_phone() -> None:
    formatter = RedactingFormatter("%(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Contact owner@example.com at +1 212-555-1234",
        args=(),
        exc_info=None,
    )

    rendered = formatter.format(record)

    assert "owner@example.com" not in rendered
    assert "+1 212-555-1234" not in rendered
    assert rendered.count("[REDACTED]") == 2
