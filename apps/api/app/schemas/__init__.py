"""Pydantic schema package for API request and response contracts."""

from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
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
    "RegisterRequest",
    "RegisterResponse",
    "RegisterStickerRequest",
    "RegisterStickerResponse",
    "RelayMessageRequest",
    "RelayMessageResponse",
    "ScanStickerRequest",
    "ScanStickerResponse",
    "TokenResponse",
]
