"""Notification adapter that logs events; replace with SMS/email providers in prod."""

import logging

logger = logging.getLogger(__name__)


class LoggingNotificationAdapter:
    """Simple notification adapter using structured logs for audit visibility."""

    async def notify_owner_lost_item_scanned(
        self, *, owner_user_id: str, item_name: str, finder_note: str | None
    ) -> None:
        """Log scan event notification for owner."""
        logger.info(
            "Owner notified about scan event",
            extra={
                "owner_user_id": owner_user_id,
                "item_name": item_name,
                "finder_note": finder_note or "",
                "event": "lost_item_scanned",
            },
        )

    async def notify_owner_new_message(self, *, owner_user_id: str, message_preview: str) -> None:
        """Log new message event for owner."""
        logger.info(
            "Owner notified about new finder message",
            extra={
                "owner_user_id": owner_user_id,
                "message_preview": message_preview,
                "event": "finder_message",
            },
        )
