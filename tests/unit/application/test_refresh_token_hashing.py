from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.application.use_cases.auth_login import AuthLoginUseCase
from app.domain.entities.user import User
from app.infrastructure.security.token_service import JwtTokenService


class FakeUow:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def __aenter__(self) -> FakeUow:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        return None

    async def commit(self) -> None:
        return None


@pytest.mark.asyncio
async def test_login_stores_only_refresh_hash_not_plain_token() -> None:
    uow = FakeUow()
    user = User(
        id="user_1",
        created_at=datetime.now(tz=UTC),
        email_encrypted="enc::owner@example.com",
        phone_encrypted=None,
        email_verified=False,
        phone_verified=False,
        status="active",
        refresh_token_hash=None,
    )
    uow.users[user.id] = user

    token_service = JwtTokenService(
        secret_key="secret",
        algorithm="HS256",
        access_token_exp_minutes=30,
        refresh_token_exp_minutes=60,
    )
    use_case = AuthLoginUseCase(uow=uow, token_service=token_service)

    result = await use_case.execute(
        email_or_phone="owner@example.com",
        otp_or_password_stub="123456",
    )

    assert user.refresh_token_hash is not None
    assert user.refresh_token_hash != result.refresh_token
    assert user.refresh_token_hash == token_service.hash_refresh(result.refresh_token)
