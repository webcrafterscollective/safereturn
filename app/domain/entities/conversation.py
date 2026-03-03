"""Owner-finder conversation entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errors import InvariantViolationError


@dataclass(slots=True)
class Conversation:
    id: str
    item_id: str
    owner_id: str
    finder_anon_id: str
    status: str
    created_at: datetime

    def __post_init__(self) -> None:
        if self.status not in {"open", "closed"}:
            raise InvariantViolationError("invalid conversation status")
