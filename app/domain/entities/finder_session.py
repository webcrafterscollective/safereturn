"""Finder session entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errors import InvariantViolationError
from app.domain.value_objects.public_token import ensure_high_entropy_public_token


@dataclass(slots=True)
class FinderSession:
    id: str
    public_token: str
    session_token: str
    expires_at: datetime
    created_at: datetime

    def __post_init__(self) -> None:
        ensure_high_entropy_public_token(self.public_token)
        if not self.session_token.strip():
            raise InvariantViolationError("session token cannot be blank")
        if self.expires_at <= self.created_at:
            raise InvariantViolationError("finder session expiry must be in the future")
