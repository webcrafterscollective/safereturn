"""Structured JSON logging with request ID correlation."""

import contextvars
import json
import logging
from datetime import UTC, datetime
from typing import Any

request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    """Format logs as JSON lines suitable for ingestion by log platforms."""

    def format(self, record: logging.LogRecord) -> str:
        """Build a JSON object with common fields and optional exception info."""
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx_var.get(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


def configure_logging(log_level: str) -> None:
    """Configure root logger once with JSON formatter.

    Args:
        log_level: String log level such as INFO or DEBUG.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())
