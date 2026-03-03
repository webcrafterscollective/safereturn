"""JWT and refresh-token hashing adapter."""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.application.errors import AuthorizationError


class JwtTokenService:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_exp_minutes: int,
        refresh_token_exp_minutes: int,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_exp_minutes = access_token_exp_minutes
        self._refresh_token_exp_minutes = refresh_token_exp_minutes

    def issue_access_refresh(self, user_id: str) -> tuple[str, str, str]:
        access_payload = {
            "sub": user_id,
            "exp": datetime.now(tz=UTC) + timedelta(minutes=self._access_token_exp_minutes),
            "typ": "access",
        }
        access_token = jwt.encode(access_payload, self._secret_key, algorithm=self._algorithm)

        refresh_suffix = secrets.token_urlsafe(12)
        refresh_token = f"refresh::{user_id}::{refresh_suffix}"
        return access_token, refresh_token, self._hash_refresh(refresh_token)

    def verify_access(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError as exc:
            raise AuthorizationError("invalid access token") from exc

        if payload.get("typ") != "access":
            raise AuthorizationError("invalid access token")

        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise AuthorizationError("invalid access token")
        return subject

    def rotate_refresh(self, refresh_token: str) -> tuple[str, str, str]:
        user_id = self.extract_user_id_from_refresh(refresh_token)
        return self.issue_access_refresh(user_id=user_id)

    @staticmethod
    def extract_user_id_from_refresh(refresh_token: str) -> str:
        parts = refresh_token.split("::")
        if len(parts) != 3 or parts[0] != "refresh":
            raise AuthorizationError("invalid refresh token")
        return parts[1]

    def hash_refresh(self, refresh_token: str) -> str:
        return self._hash_refresh(refresh_token)

    @staticmethod
    def _hash_refresh(refresh_token: str) -> str:
        return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
