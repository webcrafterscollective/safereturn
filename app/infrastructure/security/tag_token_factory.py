"""Token factory for tags and claims."""

from __future__ import annotations

import secrets


class TagTokenFactory:
    def new_public_token(self) -> str:
        return secrets.token_urlsafe(24)

    def new_claim_code(self) -> str:
        return f"CLM-{secrets.token_hex(4).upper()}"
