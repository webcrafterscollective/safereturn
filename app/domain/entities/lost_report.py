"""Lost/found status for an item."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class LostReport:
    id: str
    item_id: str
    is_lost: bool
    lost_at: datetime
    found_at: datetime | None
