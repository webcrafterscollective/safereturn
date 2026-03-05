"""Domain-level helper functions for recovery token and session rules."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe


def generate_public_session_token() -> str:
    """Generate a URL-safe token shared with finder and owner clients."""
    return token_urlsafe(24)


def hash_public_session_token(*, token: str, secret_key: str) -> str:
    """Hash session token before persistence so plaintext is never stored."""
    raw = f"{token}:{secret_key}".encode()
    return sha256(raw).hexdigest()


def compute_session_expiry(*, ttl_minutes: int) -> datetime:
    """Return UTC expiry timestamp for a finder session."""
    return datetime.now(UTC) + timedelta(minutes=ttl_minutes)


def is_session_expired(*, expires_at: datetime) -> bool:
    """Return True if the session has already expired in UTC time."""
    normalized_expiry = (
        expires_at if expires_at.tzinfo is not None else expires_at.replace(tzinfo=UTC)
    )
    return datetime.now(UTC) >= normalized_expiry
