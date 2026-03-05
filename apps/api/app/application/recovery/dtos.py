"""Typed DTOs exchanged between interface layer and recovery use cases."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.recovery.entities import SenderRole


@dataclass(slots=True, frozen=True)
class RegisterStickerCommand:
    """Input payload to create item and sticker mapping."""

    owner_user_id: str
    sticker_code: str
    item_name: str
    item_category: str
    item_description: str


@dataclass(slots=True, frozen=True)
class MarkItemLostCommand:
    """Input payload to mark an owner item as lost and open a report."""

    owner_user_id: str
    item_id: str
    last_known_location: str | None
    notes: str | None


@dataclass(slots=True, frozen=True)
class StartFinderSessionCommand:
    """Input payload to open a finder session from scanned sticker code."""

    sticker_code: str
    finder_note: str | None
    finder_ip: str | None


@dataclass(slots=True, frozen=True)
class RelayMessageCommand:
    """Input payload to relay finder/owner message in an anonymous session."""

    session_token: str
    sender_role: SenderRole
    message_body: str
    owner_user_id: str | None = None


@dataclass(slots=True, frozen=True)
class FinderSessionDTO:
    """Session details returned to finder client after scan."""

    session_token: str
    item_name: str
    owner_hint: str
    expires_at: datetime


@dataclass(slots=True, frozen=True)
class RegisteredStickerDTO:
    """Confirmation payload returned after sticker registration."""

    item_id: str
    sticker_code: str
    status: str


@dataclass(slots=True, frozen=True)
class RelayMessageDTO:
    """Single message record rendered in finder/owner inbox."""

    session_reference: str
    sender_role: SenderRole
    body: str
    created_at: datetime


@dataclass(slots=True, frozen=True)
class LostReportDTO:
    """Lost report summary returned after mark-lost call."""

    report_id: str
    item_id: str
    status: str
    created_at: datetime
