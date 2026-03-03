"""Shared domain entity base helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class AuditedEntity:
    """Simple base for entities with creation timestamp."""

    created_at: datetime

    @classmethod
    def now(cls) -> datetime:
        return datetime.now(tz=UTC)
