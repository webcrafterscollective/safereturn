from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import NotFoundError


@dataclass(slots=True)
class TagsClaimResult:
    tag_id: str
    public_token: str


class TagsClaimUseCase:
    def __init__(self, uow) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow

    async def execute(self, user_id: str, claim_code: str) -> TagsClaimResult:
        async with self._uow:
            for tag in self._uow.tags.values():
                if tag.claim_code == claim_code and tag.status == "unclaimed":
                    tag.owner_id = user_id
                    tag.status = "claimed"
                    await self._uow.commit()
                    return TagsClaimResult(tag_id=tag.id, public_token=tag.public_token)
            raise NotFoundError("claim code not found")
