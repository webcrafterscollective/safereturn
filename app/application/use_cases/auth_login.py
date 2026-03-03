from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from app.application.errors import AuthorizationError
from app.application.ports.security.security_ports import EncryptionPort, TokenServicePort
from app.domain.entities.user import User


@dataclass(slots=True)
class AuthLoginResult:
    access_token: str
    refresh_token: str


class AuthLoginUseCase:
    def __init__(
        self,
        uow: Any,
        token_service: TokenServicePort,
        encryption: EncryptionPort | None = None,
    ) -> None:
        self._uow = uow
        self._token_service = token_service
        self._encryption = encryption

    async def execute(self, email_or_phone: str, otp_or_password_stub: str) -> AuthLoginResult:
        _ = otp_or_password_stub
        async with self._uow:
            user = self._find_by_identifier(email_or_phone)
            access_token, refresh_token, refresh_hash = self._token_service.issue_access_refresh(
                user_id=user.id
            )
            user.refresh_token_hash = refresh_hash
            await self._uow.commit()
            return AuthLoginResult(access_token=access_token, refresh_token=refresh_token)

    def _find_by_identifier(self, value: str) -> User:
        for unknown_user in self._uow.users.values():
            user = cast(User, unknown_user)
            if user.email_encrypted:
                if self._matches_identifier(encrypted=user.email_encrypted, raw=value):
                    return user
            if user.phone_encrypted:
                if self._matches_identifier(encrypted=user.phone_encrypted, raw=value):
                    return user
        raise AuthorizationError("invalid credentials")

    def _matches_identifier(self, encrypted: str, raw: str) -> bool:
        if self._encryption is not None:
            try:
                return self._encryption.decrypt(encrypted) == raw
            except Exception:  # pragma: no cover - defensive path
                return False
        return encrypted.endswith(raw)
