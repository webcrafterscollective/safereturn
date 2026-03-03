from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AuthLogoutResult:
    success: bool


class AuthLogoutUseCase:
    def __init__(self, uow) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow

    async def execute(self, user_id: str) -> AuthLogoutResult:
        async with self._uow:
            user = self._uow.users.get(user_id)
            if user:
                user.refresh_token_hash = None
            await self._uow.commit()
            return AuthLogoutResult(success=True)
