from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.tag import Tag


@dataclass(slots=True)
class BatchTagItem:
    tag_id: str
    claim_code: str
    public_token: str


@dataclass(slots=True)
class BatchCreateTagsResult:
    tags: list[BatchTagItem]


class AdminBatchCreateTagsUseCase:
    def __init__(self, uow, id_generator, clock, token_factory) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock
        self._token_factory = token_factory

    async def execute(self, count: int) -> BatchCreateTagsResult:
        async with self._uow:
            tags: list[BatchTagItem] = []
            for _ in range(count):
                tag_id = self._id_generator.new_id()
                claim_code = self._token_factory.new_claim_code()
                public_token = self._token_factory.new_public_token()
                tag = Tag(
                    id=tag_id,
                    public_token=public_token,
                    claim_code=claim_code,
                    status="unclaimed",
                    owner_id=None,
                    created_at=self._clock.now(),
                )
                self._uow.tags[tag.id] = tag
                tags.append(
                    BatchTagItem(
                        tag_id=tag.id, claim_code=tag.claim_code, public_token=tag.public_token
                    )
                )
            await self._uow.commit()
            return BatchCreateTagsResult(tags=tags)
