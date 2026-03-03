"""Token-related value object rules."""

from __future__ import annotations

import base64

from app.domain.errors import InvariantViolationError


def ensure_high_entropy_public_token(token: str) -> None:
    """Validate that a token provides at least 128 bits of entropy.

    Accepts url-safe base64 token strings as used in QR links.
    """

    normalized = token.strip()
    if not normalized:
        raise InvariantViolationError("public token cannot be blank")

    padding = "=" * (-len(normalized) % 4)
    try:
        decoded = base64.urlsafe_b64decode(normalized + padding)
    except Exception as exc:  # pragma: no cover - defensive branch
        raise InvariantViolationError("public token format is invalid") from exc

    if len(decoded) < 16:
        raise InvariantViolationError("public token must have at least 128-bit entropy")
