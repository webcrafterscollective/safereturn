"""Domain entities and enums for the SafeReturn lost-item recovery flow."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class StickerStatus(StrEnum):
    """Lifecycle states for a QR sticker."""

    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    LOST = "lost"
    RECOVERED = "recovered"
    DISABLED = "disabled"


class LostReportStatus(StrEnum):
    """Lifecycle states for a lost-item report."""

    OPEN = "open"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class SenderRole(StrEnum):
    """Supported sender roles in the anonymous relay."""

    FINDER = "finder"
    OWNER = "owner"


@dataclass(slots=True, frozen=True)
class Item:
    """Owner-registered item to which a sticker can be attached."""

    id: str
    owner_user_id: str
    display_name: str
    category: str
    description: str
    is_lost: bool
    created_at: datetime


@dataclass(slots=True, frozen=True)
class QRSticker:
    """QR sticker assigned to one item and used to create finder sessions."""

    id: str
    code: str
    owner_user_id: str
    item_id: str | None
    status: StickerStatus
    created_at: datetime


@dataclass(slots=True, frozen=True)
class FinderSession:
    """Short-lived session started when a finder scans a QR code."""

    id: str
    sticker_id: str
    public_token: str
    expires_at: datetime
    created_at: datetime
    finder_note: str | None


@dataclass(slots=True, frozen=True)
class AnonymousMessage:
    """Message relayed between finder and owner without exposing identity."""

    id: str
    finder_session_id: str
    sender_role: SenderRole
    body: str
    created_at: datetime


@dataclass(slots=True, frozen=True)
class LostItemReport:
    """Report raised by owner when an item is marked as lost."""

    id: str
    item_id: str
    owner_user_id: str
    status: LostReportStatus
    last_known_location: str | None
    notes: str | None
    created_at: datetime
