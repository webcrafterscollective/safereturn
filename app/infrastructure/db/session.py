"""Database session factory."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import get_settings


def create_engine(database_url: str | None = None) -> AsyncEngine:
    url = database_url or get_settings().database_url
    return create_async_engine(url, echo=False)


def create_session_factory(database_url: str | None = None) -> async_sessionmaker[AsyncSession]:
    engine = create_engine(database_url=database_url)
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
