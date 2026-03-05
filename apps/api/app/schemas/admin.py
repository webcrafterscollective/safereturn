"""Admin API schemas for sticker-pack operations and platform-level management."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.recovery import StickerSummary


class GeneratePackRequest(BaseModel):
    """Request payload to create a printable sticker pack."""

    quantity: int = Field(ge=1, le=500, examples=[10])


class StickerPackSummary(BaseModel):
    """Sticker pack metadata returned in admin listings."""

    id: str
    pack_code: str
    total_stickers: int
    status: str
    assigned_user_id: str | None
    created_at: datetime
    claimed_at: datetime | None


class GeneratePackResponse(BaseModel):
    """Response payload after creating one sticker pack."""

    pack: StickerPackSummary
    stickers: list[StickerSummary]


class ListPacksResponse(BaseModel):
    """Response for admin pack inventory list."""

    packs: list[StickerPackSummary]


class PackStickersResponse(BaseModel):
    """Response for all stickers in one selected pack."""

    pack: StickerPackSummary
    stickers: list[StickerSummary]


class CreateUserAndAssignPackRequest(BaseModel):
    """Admin request to create owner account and optionally assign a pack."""

    email: EmailStr = Field(examples=["owner@example.com"])
    password: str = Field(min_length=8, max_length=128)
    pack_code: str | None = Field(default=None, max_length=64)


class CreateUserAndAssignPackResponse(BaseModel):
    """Result of admin user provisioning flow."""

    user_id: str
    email: EmailStr
    assigned_pack_code: str | None


class AdminOverviewResponse(BaseModel):
    """Top-level counters for admin portal dashboard."""

    users: int
    packs: int
    stickers: int
    claimed_packs: int
    unassigned_stickers: int
