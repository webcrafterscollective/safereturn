"""Notification adapters for mocked channels."""

from __future__ import annotations


class MockNotificationAdapter:
    def __init__(self) -> None:
        self.sent_events: list[dict[str, str]] = []

    async def send(self, to_user_id: str, event_type: str, payload: dict[str, str]) -> None:
        self.sent_events.append(
            {
                "to_user_id": to_user_id,
                "event_type": event_type,
                "payload": str(payload),
            }
        )
