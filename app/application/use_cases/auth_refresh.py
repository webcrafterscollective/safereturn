from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import AuthorizationError


@dataclass(slots=True)
class AuthRefreshResult:
    access_token: str
    refresh_token: str


class AuthRefreshUseCase:
    def __init__(self, uow, token_service) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._token_service = token_service

    async def execute(self, refresh_token: str) -> AuthRefreshResult:
        async with self._uow:
            if hasattr(self._token_service, "extract_user_id_from_refresh"):
                user_id = self._token_service.extract_user_id_from_refresh(refresh_token)
            else:
                user_id = refresh_token.removeprefix("refresh-")
            user = self._uow.users.get(user_id)
            expected_hash = (
                self._token_service.hash_refresh(refresh_token)
                if hasattr(self._token_service, "hash_refresh")
                else None
            )
            if (
                not user
                or not user.refresh_token_hash
                or (expected_hash is not None and user.refresh_token_hash != expected_hash)
            ):
                raise AuthorizationError("invalid refresh token")
            access_token, rotated_refresh_token, new_hash = self._token_service.rotate_refresh(
                refresh_token
            )
            user.refresh_token_hash = new_hash
            await self._uow.commit()
            return AuthRefreshResult(
                access_token=access_token,
                refresh_token=rotated_refresh_token,
            )
