"""User aggregate root."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errors import InvariantViolationError


@dataclass(slots=True)
class User:
    id: str
    created_at: datetime
    email_encrypted: str | None
    phone_encrypted: str | None
    email_verified: bool
    phone_verified: bool
    status: str
    refresh_token_hash: str | None

    def __post_init__(self) -> None:
        if not self.email_encrypted and not self.phone_encrypted:
            raise InvariantViolationError(
                "user must have at least one contact method for notifications"
            )
        if self.status not in {"active", "disabled"}:
            raise InvariantViolationError("invalid user status")
