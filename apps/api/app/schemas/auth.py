"""Authentication API schemas for login, refresh, and token responses."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request payload with email/password credentials."""

    email: EmailStr = Field(examples=["user@example.com"])
    password: str = Field(min_length=8, examples=["strong-password"])


class RegisterRequest(BaseModel):
    """Registration payload for creating a new owner account."""

    email: EmailStr = Field(examples=["owner@example.com"])
    password: str = Field(min_length=8, examples=["strong-password"])


class RefreshRequest(BaseModel):
    """Refresh request payload containing refresh token."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request payload containing refresh token to revoke."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Token response returned after login or refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RegisterResponse(BaseModel):
    """Registration response returned after account creation."""

    user_id: str
    email: EmailStr
