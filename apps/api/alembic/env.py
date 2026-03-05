"""Alembic environment setup with async engine support and autogenerate metadata."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from app.core.settings import get_settings
from app.db.base import Base
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.user import User
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models so metadata includes every table.
_ = (User, RefreshToken, AuditLog)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode using URL only."""
    settings = get_settings()
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with active DB connection."""
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode using async engine."""
    settings = get_settings()
    section = config.get_section(config.config_ini_section)
    if section is None:
        section = {}
    section["sqlalchemy.url"] = settings.database_url

    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def run() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    import asyncio

    asyncio.run(run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
