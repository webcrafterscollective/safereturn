from __future__ import annotations

from pydantic import BaseModel


class AuthRegisterRequest(BaseModel):
    email: str | None = None
    phone: str | None = None


class AuthRegisterResponse(BaseModel):
    user_id: str


class AuthLoginRequest(BaseModel):
    email_or_phone: str
    otp_or_password_stub: str


class AuthTokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str


class AuthRefreshRequest(BaseModel):
    refresh_token: str


class AuthLogoutResponse(BaseModel):
    success: bool
