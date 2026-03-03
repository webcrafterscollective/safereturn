from __future__ import annotations

from app.infrastructure.security.encryption import FernetEncryptionAdapter


def test_fernet_encryption_roundtrip() -> None:
    adapter = FernetEncryptionAdapter("xVdY8US9hQFoY8A9HtV6nRvWmvMRGsiE9zMDFMvx6bM=")

    encrypted = adapter.encrypt("owner@example.com")

    assert encrypted != "owner@example.com"
    assert adapter.decrypt(encrypted) == "owner@example.com"
