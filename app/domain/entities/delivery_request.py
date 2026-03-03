"""Delivery request entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errors import InvariantViolationError

_ALLOWED_STATES = {"created", "booked", "picked_up", "delivered", "canceled"}


@dataclass(slots=True)
class DeliveryRequest:
    id: str
    conversation_id: str
    status: str
    provider: str
    provider_ref: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_STATES:
            raise InvariantViolationError("invalid delivery request status")
