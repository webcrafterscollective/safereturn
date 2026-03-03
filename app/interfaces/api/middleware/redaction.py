"""Request logging redaction helpers."""

from __future__ import annotations

import logging
import re

REDACTION_PATTERNS = [
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    re.compile(r"\+?\d[\d\s-]{7,}\d"),
]


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        for pattern in REDACTION_PATTERNS:
            rendered = pattern.sub("[REDACTED]", rendered)
        return rendered
