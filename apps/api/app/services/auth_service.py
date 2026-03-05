"""Authentication service with login, refresh rotation, and logout logic."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    TokenError,
    create_jwt_token,
    decode_jwt_token,
    hash_refresh_token,
    verify_password,
)
from app.core.settings import Settings
from app.repositories.token_repo import TokenRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    """Encapsulates authentication business rules and token lifecycle."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.user_repo = UserRepository(session)
        self.token_repo = TokenRepository(session)

    async def authenticate_user(self, *, email: str, password: str) -> str:
        """Validate user credentials and return user id.

        Raises:
            AppError: If credentials are invalid.
        """
        user = await self.user_repo.get_by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            raise AppError(
                code="INVALID_CREDENTIALS",
                message="Invalid email or password",
                status_code=401,
            )
        return user.id

    async def issue_tokens(self, *, user_id: str) -> TokenResponse:
        """Issue new access/refresh tokens and persist hashed refresh token."""
        access_expires = timedelta(minutes=self.settings.access_token_ttl_minutes)
        refresh_expires = timedelta(days=self.settings.refresh_token_ttl_days)

        access_token = create_jwt_token(
            settings=self.settings,
            subject=user_id,
            token_type=ACCESS_TOKEN_TYPE,
            expires_delta=access_expires,
        )
        refresh_token = create_jwt_token(
            settings=self.settings,
            subject=user_id,
            token_type=REFRESH_TOKEN_TYPE,
            expires_delta=refresh_expires,
        )

        refresh_expiry_time = datetime.now(UTC) + refresh_expires
        refresh_hash = hash_refresh_token(token=refresh_token, settings=self.settings)
        await self.token_repo.store_refresh_token_hash(
            user_id=user_id,
            token_hash=refresh_hash,
            expires_at=refresh_expiry_time,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.settings.access_token_ttl_minutes * 60,
        )

    async def refresh_tokens(self, *, refresh_token: str) -> TokenResponse:
        """Rotate refresh token and issue a fresh access/refresh pair."""
        try:
            payload = decode_jwt_token(
                token=refresh_token,
                settings=self.settings,
                expected_type=REFRESH_TOKEN_TYPE,
            )
        except TokenError as exc:
            raise AppError(
                code="INVALID_REFRESH_TOKEN",
                message="Refresh token is invalid",
                status_code=401,
            ) from exc

        token_hash = hash_refresh_token(token=refresh_token, settings=self.settings)
        stored_token = await self.token_repo.validate_token(token_hash=token_hash)
        if stored_token is None:
            raise AppError(
                code="INVALID_REFRESH_TOKEN",
                message="Refresh token is invalid or revoked",
                status_code=401,
            )

        revoked = await self.token_repo.revoke_token(token_hash=token_hash)
        if not revoked:
            raise AppError(
                code="INVALID_REFRESH_TOKEN",
                message="Refresh token is invalid",
                status_code=401,
            )

        user_id = str(payload.get("sub", ""))
        if not user_id:
            raise AppError(
                code="INVALID_REFRESH_TOKEN",
                message="Refresh token payload is invalid",
                status_code=401,
            )

        return await self.issue_tokens(user_id=user_id)

    async def logout(self, *, refresh_token: str) -> None:
        """Revoke refresh token so it can no longer be used."""
        token_hash = hash_refresh_token(token=refresh_token, settings=self.settings)
        await self.token_repo.revoke_token(token_hash=token_hash)
