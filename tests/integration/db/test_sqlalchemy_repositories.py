from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.entities.tag import Tag
from app.domain.entities.user import User
from app.infrastructure.db.base import Base
from app.infrastructure.repositories.tag_repository import SqlAlchemyTagRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


@pytest.mark.asyncio
async def test_user_repository_add_and_get() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        repository = SqlAlchemyUserRepository(session)
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
        await repository.add(user)
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemyUserRepository(session)
        loaded = await repository.get_by_id("user_1")
        assert loaded is not None
        assert loaded.email_encrypted == "enc::owner@example.com"


@pytest.mark.asyncio
async def test_tag_repository_find_by_public_token() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        repository = SqlAlchemyTagRepository(session)
        tag = Tag(
            id="tag_1",
            public_token="vQ6W2xkR3M7qYp8hNu4zDw",
            claim_code="CLAIM-001",
            status="unclaimed",
            owner_id=None,
            created_at=datetime.now(tz=UTC),
        )
        await repository.add(tag)
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemyTagRepository(session)
        loaded = await repository.get_by_public_token("vQ6W2xkR3M7qYp8hNu4zDw")
        assert loaded is not None
        assert loaded.claim_code == "CLAIM-001"
