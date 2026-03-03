"""Application configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QR Lost & Found"
    environment: str = "dev"
    database_url: str = "postgresql+asyncpg://lostfound:lostfound@localhost:5432/lostfound"
    test_database_url: str = "sqlite+aiosqlite:///:memory:"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_exp_minutes: int = 30
    refresh_token_exp_minutes: int = 60 * 24 * 7
    fernet_key: str = "xVdY8US9hQFoY8A9HtV6nRvWmvMRGsiE9zMDFMvx6bM="
    admin_api_key: str = "dev-admin-key"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
