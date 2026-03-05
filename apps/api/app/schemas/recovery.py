"""API schemas for QR registration, scan sessions, and anonymous relay messaging."""

from datetime import datetime

from pydantic import BaseModel, Field


class RegisterStickerRequest(BaseModel):
    """Owner request to register a sticker and attach it to an item."""

    sticker_code: str = Field(min_length=3, max_length=64, examples=["SAFE-ABCD-001"])
    item_name: str = Field(min_length=1, max_length=120, examples=["Black Laptop Bag"])
    item_category: str = Field(min_length=1, max_length=80, examples=["bag"])
    item_description: str = Field(
        default="",
        max_length=500,
        examples=["Contains office laptop and notebook"],
    )


class RegisterStickerResponse(BaseModel):
    """Registration confirmation response."""

    item_id: str
    sticker_code: str
    status: str


class MarkItemLostRequest(BaseModel):
    """Owner request to mark an item as lost."""

    last_known_location: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=1000)


class LostReportResponse(BaseModel):
    """Lost report creation response."""

    report_id: str
    item_id: str
    status: str
    created_at: datetime


class ScanStickerRequest(BaseModel):
    """Finder request used after scanning a sticker QR code."""

    sticker_code: str = Field(min_length=3, max_length=64)
    finder_note: str | None = Field(default=None, max_length=500)


class ScanStickerResponse(BaseModel):
    """Finder session bootstrap payload."""

    session_token: str
    item_name: str
    owner_hint: str
    expires_at: datetime


class RelayMessageRequest(BaseModel):
    """Message payload used by finder and owner relay endpoints."""

    message_body: str = Field(min_length=1, max_length=2000)


class RelayMessageResponse(BaseModel):
    """Relay message response with sender and timestamp."""

    session_reference: str
    sender_role: str
    body: str
    created_at: datetime


class OwnerInboxResponse(BaseModel):
    """Owner inbox listing relay messages across active sessions."""

    messages: list[RelayMessageResponse]


class ClaimPackRequest(BaseModel):
    """Request payload for claiming a sticker pack by printed pack code."""

    pack_code: str = Field(min_length=3, max_length=64, examples=["PACK-1A2B3C4D"])


class StickerSummary(BaseModel):
    """Compact sticker payload rendered in owner/admin dashboards."""

    code: str
    status: str
    item_id: str | None
    assigned_once: bool
    claimed_at: datetime | None
    invalidated_at: datetime | None
    replaced_by_code: str | None
    qr_scan_url: str


class ClaimPackResponse(BaseModel):
    """Response after successful pack claim."""

    pack_code: str
    total_stickers: int
    stickers: list[StickerSummary]


class UserStickersResponse(BaseModel):
    """Owner sticker inventory listing."""

    stickers: list[StickerSummary]


class OwnerItemSummary(BaseModel):
    """Owner item record with linked sticker state for dashboard tracking."""

    item_id: str
    item_name: str
    category: str
    description: str
    is_lost: bool
    sticker_code: str | None
    sticker_status: str | None
    created_at: datetime


class UserItemsResponse(BaseModel):
    """Owner item inventory listing."""

    items: list[OwnerItemSummary]


class RegenerateStickerResponse(BaseModel):
    """Response containing replacement sticker details."""

    replaced_code: str
    replacement: StickerSummary


class ClaimIssueRequest(BaseModel):
    """Support ticket payload when user receives already-claimed sticker."""

    sticker_code: str = Field(min_length=3, max_length=64)
    note: str = Field(min_length=5, max_length=500)


class ClaimIssueResponse(BaseModel):
    """Support ticket creation response."""

    audit_event_id: int
    message: str
