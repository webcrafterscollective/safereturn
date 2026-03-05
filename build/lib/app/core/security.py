"""Security utilities for password hashing and JWT handling."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.settings import Settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
ALGORITHM = "HS256"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenError(Exception):
    """Raised when a token is invalid or fails validation checks."""


def hash_password(raw_password: str) -> str:
    """Hash plaintext password using bcrypt.

    Args:
        raw_password: User-supplied plaintext password.

    Returns:
        Hashed password string safe to store in database.
    """
    return password_context.hash(raw_password)


def verify_password(raw_password: str, password_hash: str) -> bool:
    """Verify plaintext password against stored hash."""
    return password_context.verify(raw_password, password_hash)


def create_jwt_token(
    *,
    settings: Settings,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create signed JWT token with standard auth claims.

    Args:
        settings: App settings containing signing secret.
        subject: Subject claim (usually user id).
        token_type: access or refresh.
        expires_delta: Token validity window.
        extra_claims: Optional additional claims.

    Returns:
        Signed JWT string.
    """
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": str(uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_jwt_token(*, token: str, settings: Settings, expected_type: str) -> dict[str, Any]:
    """Decode and validate JWT token type.

    Raises:
        TokenError: If token is expired, malformed, or type does not match.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise TokenError("Token decode failed") from exc

    token_type = payload.get("type")
    if token_type != expected_type:
        raise TokenError("Token type mismatch")

    return payload


def hash_refresh_token(*, token: str, settings: Settings) -> str:
    """Hash refresh token with app secret for safe DB storage.

    This prevents plaintext refresh tokens from being stored server-side.
    """
    raw = f"{token}:{settings.secret_key}".encode()
    return sha256(raw).hexdigest()
