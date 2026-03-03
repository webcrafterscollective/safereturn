from __future__ import annotations

from typing import Protocol


class NotificationPort(Protocol):
    async def send(self, to_user_id: str, event_type: str, payload: dict[str, str]) -> None: ...
