"""Pydantic schema package for API request and response contracts."""

from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse
from app.schemas.recovery import (
    LostReportResponse,
    MarkItemLostRequest,
    OwnerInboxResponse,
    RegisterStickerRequest,
    RegisterStickerResponse,
    RelayMessageRequest,
    RelayMessageResponse,
    ScanStickerRequest,
    ScanStickerResponse,
)

__all__ = [
    "LoginRequest",
    "LogoutRequest",
    "LostReportResponse",
    "MarkItemLostRequest",
    "OwnerInboxResponse",
    "RefreshRequest",
    "RegisterStickerRequest",
    "RegisterStickerResponse",
    "RelayMessageRequest",
    "RelayMessageResponse",
    "ScanStickerRequest",
    "ScanStickerResponse",
    "TokenResponse",
]
