"""Application settings loaded from environment variables.

This module centralizes every configurable value so the app is 12-factor ready.
Each field maps to an env var and has safe defaults for local development.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for API, database, security, and frontend serving.

    Env vars:
    - APP_NAME: Human-readable app name.
    - ENVIRONMENT: dev/staging/prod flag used for behavior toggles.
    - LOG_LEVEL: Standard log verbosity (DEBUG, INFO, WARNING, ERROR).
    - JWT_SECRET: Secret key used to sign and verify JWT tokens.
    - SECRET_KEY: Extra app secret for future crypto usage.
    - ACCESS_TOKEN_TTL_MINUTES: Access token lifetime in minutes.
    - REFRESH_TOKEN_TTL_DAYS: Refresh token lifetime in days.
    - DATABASE_URL: SQLAlchemy URL. Example: postgresql+asyncpg://user:pass@host:5432/db
    - CORS_ALLOWED_ORIGINS: Comma-separated allowed browser origins.
    - TRUSTED_HOSTS: Comma-separated trusted hostnames.
    - PROMETHEUS_ENABLED: Enable or disable /metrics endpoint.
    - REQUEST_TIMEOUT_SECONDS: Request timeout budget for future middleware/hooks.
    - FINDER_SESSION_TTL_MINUTES: Session lifetime for anonymous finder links.
    - FRONTEND_DIST_PATH: Absolute or relative path to frontend dist assets.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="fastapi-fullstack-prod", alias="APP_NAME")
    environment: str = Field(default="dev", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    secret_key: str = Field(default="change-me-too", alias="SECRET_KEY")
    access_token_ttl_minutes: int = Field(default=15, alias="ACCESS_TOKEN_TTL_MINUTES")
    refresh_token_ttl_days: int = Field(default=7, alias="REFRESH_TOKEN_TTL_DAYS")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./local.db",
        alias="DATABASE_URL",
    )

    cors_allowed_origins: str = Field(default="http://localhost:8000", alias="CORS_ALLOWED_ORIGINS")
    trusted_hosts: str = Field(default="localhost,127.0.0.1", alias="TRUSTED_HOSTS")

    prometheus_enabled: bool = Field(default=True, alias="PROMETHEUS_ENABLED")
    request_timeout_seconds: int = Field(default=30, alias="REQUEST_TIMEOUT_SECONDS")
    finder_session_ttl_minutes: int = Field(default=60, alias="FINDER_SESSION_TTL_MINUTES")

    frontend_dist_path: str = Field(default="", alias="FRONTEND_DIST_PATH")

    @property
    def cors_origins_list(self) -> list[str]:
        """Return parsed CORS origins list without empty items."""
        return [item.strip() for item in self.cors_allowed_origins.split(",") if item.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        """Return parsed TrustedHost list without empty items."""
        return [item.strip() for item in self.trusted_hosts.split(",") if item.strip()]

    @property
    def computed_frontend_dist_path(self) -> Path:
        """Return frontend dist path from env override or repository-relative default."""
        if self.frontend_dist_path:
            return Path(self.frontend_dist_path)
        return Path(__file__).resolve().parents[3] / "web" / "dist"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance for application lifetime."""
    return Settings()
