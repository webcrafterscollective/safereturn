"""Security-safe event log entry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AuditLog:
    id: str
    actor_type: str
    actor_id: str | None
    action: str
    metadata: dict[str, str]
    created_at: datetime
