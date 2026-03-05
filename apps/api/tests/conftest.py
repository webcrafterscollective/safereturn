"""Pytest fixtures for FastAPI async integration tests."""

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Configure deterministic test env before importing application modules.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-jwt-secret"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["TRUSTED_HOSTS"] = "testserver,localhost,127.0.0.1"
os.environ["CORS_ALLOWED_ORIGINS"] = "http://testserver"

from app.core.settings import get_settings

# Ensure settings cache reflects test env values before app imports.
get_settings.cache_clear()

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repo import UserRepository


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create SQLite test engine and schema once for test session."""
    # Import models to ensure metadata is complete for create_all.
    _ = (User, RefreshToken, AuditLog)

    engine: AsyncEngine = create_async_engine(os.environ["DATABASE_URL"], future=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
async def session_maker(test_engine) -> async_sessionmaker[AsyncSession]:
    """Provide session factory bound to test engine."""
    return async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture()
async def async_client(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    """Provide HTTP client with DB dependency overridden to test session."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture()
async def sample_user(session_maker: async_sessionmaker[AsyncSession]) -> dict[str, str]:
    """Create sample user fixture used by auth flow tests."""
    email = "test.user@example.com"
    password = "password123"

    async with session_maker() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_email(email)
        if existing is None:
            await repo.create_user(email=email, password_hash=hash_password(password))

    return {"email": email, "password": password}
