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
