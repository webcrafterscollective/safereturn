from __future__ import annotations

from typing import Protocol


class TokenServicePort(Protocol):
    def issue_access_refresh(self, user_id: str) -> tuple[str, str, str]: ...

    def verify_access(self, token: str) -> str: ...

    def rotate_refresh(self, refresh_token: str) -> tuple[str, str, str]: ...


class EncryptionPort(Protocol):
    def encrypt(self, value: str) -> str: ...

    def decrypt(self, value: str) -> str: ...


class RateLimiterPort(Protocol):
    def allow(self, key: str, limit: int, window_seconds: int) -> bool: ...
