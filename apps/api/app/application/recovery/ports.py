"""Application ports for dependency inversion in recovery use cases."""

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from app.domain.recovery.entities import (
    AnonymousMessage,
    FinderSession,
    Item,
    LostItemReport,
    QRSticker,
    SenderRole,
    StickerStatus,
)


class RecoveryRepositoryPort(Protocol):
    """Persistence contract required by recovery use cases."""

    async def get_sticker_by_code(self, *, code: str) -> QRSticker | None:
        """Fetch sticker by human-readable QR code."""

    async def get_sticker_by_item_id(self, *, item_id: str) -> QRSticker | None:
        """Fetch sticker currently attached to an item."""

    async def create_item_for_owner(
        self,
        *,
        owner_user_id: str,
        display_name: str,
        category: str,
        description: str,
    ) -> Item:
        """Persist owner item."""

    async def attach_sticker_to_item(
        self,
        *,
        sticker_code: str,
        owner_user_id: str,
        item_id: str,
    ) -> QRSticker | None:
        """Attach claimed sticker to owner item if sticker is still eligible."""

    async def set_item_lost_state(
        self, *, owner_user_id: str, item_id: str, is_lost: bool
    ) -> Item | None:
        """Update item lost flag while enforcing owner ownership."""

    async def create_lost_report(
        self,
        *,
        owner_user_id: str,
        item_id: str,
        status: str,
        last_known_location: str | None,
        notes: str | None,
    ) -> LostItemReport:
        """Persist lost item report."""

    async def set_sticker_status(self, *, sticker_id: str, status: StickerStatus) -> None:
        """Update sticker status."""

    async def create_finder_session(
        self,
        *,
        sticker_id: str,
        public_token_hash: str,
        expires_at: datetime,
        finder_note: str | None,
    ) -> FinderSession:
        """Persist finder session and return public-facing representation."""

    async def get_finder_session_by_token_hash(self, *, token_hash: str) -> FinderSession | None:
        """Load active finder session by hashed token."""

    async def get_finder_session_by_id(self, *, finder_session_id: str) -> FinderSession | None:
        """Load finder session by internal id reference."""

    async def get_item_for_session(self, *, finder_session_id: str) -> Item | None:
        """Fetch related item for a finder session."""

    async def create_anonymous_message(
        self,
        *,
        finder_session_id: str,
        sender_role: SenderRole,
        body: str,
    ) -> AnonymousMessage:
        """Persist relay message."""

    async def list_owner_messages(self, *, owner_user_id: str) -> Sequence[AnonymousMessage]:
        """List owner-visible messages across all sessions."""

    async def verify_owner_can_access_session(
        self, *, owner_user_id: str, finder_session_id: str
    ) -> bool:
        """Check ownership guard before owner sends/reads messages."""


class NotificationPort(Protocol):
    """Notification contract for owner event delivery."""

    async def notify_owner_lost_item_scanned(
        self, *, owner_user_id: str, item_name: str, finder_note: str | None
    ) -> None:
        """Notify owner that a finder scanned their sticker."""

    async def notify_owner_new_message(self, *, owner_user_id: str, message_preview: str) -> None:
        """Notify owner about a new finder message."""
