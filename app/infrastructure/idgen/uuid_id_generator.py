"""UUID-based identifier adapter."""

from __future__ import annotations

from uuid import uuid4


class UuidIdGenerator:
    def new_id(self) -> str:
        return uuid4().hex
