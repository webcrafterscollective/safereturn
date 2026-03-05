"""Repository for refresh token storage and revocation checks."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class TokenRepository:
    """Data access object for refresh token lifecycle."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def store_refresh_token_hash(
        self,
        *,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Persist a newly issued refresh token hash."""
        record = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def revoke_token(self, *, token_hash: str) -> bool:
        """Mark token as revoked.

        Returns True when a token was found and revoked, else False.
        """
        token = await self.validate_token(token_hash=token_hash)
        if token is None:
            return False

        token.revoked_at = datetime.now(UTC)
        await self.session.commit()
        return True

    async def validate_token(self, *, token_hash: str) -> RefreshToken | None:
        """Return active token record when present and not expired/revoked."""
        now = datetime.now(UTC)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
