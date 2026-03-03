from __future__ import annotations

from typing import Protocol

from app.domain.entities.user import User


class UserRepository(Protocol):
    async def add(self, user: User) -> None: ...

    async def get_by_id(self, user_id: str) -> User | None: ...
