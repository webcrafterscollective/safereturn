"""Owner item entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errors import InvariantViolationError


@dataclass(slots=True)
class Item:
    id: str
    owner_id: str
    tag_id: str
    name: str
    category: str
    notes: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("item name cannot be blank")
        if not self.category.strip():
            raise InvariantViolationError("item category cannot be blank")
