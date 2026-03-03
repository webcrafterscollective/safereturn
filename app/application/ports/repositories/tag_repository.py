from __future__ import annotations

from typing import Protocol

from app.domain.entities.tag import Tag


class TagRepository(Protocol):
    async def add(self, tag: Tag) -> None: ...

    async def get_by_public_token(self, public_token: str) -> Tag | None: ...
