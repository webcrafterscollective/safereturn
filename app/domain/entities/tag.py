"""Tag aggregate entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errors import InvariantViolationError
from app.domain.value_objects.public_token import ensure_high_entropy_public_token


@dataclass(slots=True)
class Tag:
    id: str
    public_token: str
    claim_code: str
    status: str
    owner_id: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        ensure_high_entropy_public_token(self.public_token)
        if not self.claim_code.strip():
            raise InvariantViolationError("claim code cannot be blank")
        if self.status not in {"unclaimed", "claimed", "disabled"}:
            raise InvariantViolationError("tag status is invalid")
