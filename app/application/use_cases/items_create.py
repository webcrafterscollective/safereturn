from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import AuthorizationError, NotFoundError
from app.domain.entities.item import Item


@dataclass(slots=True)
class ItemsCreateResult:
    item_id: str


class ItemsCreateUseCase:
    def __init__(self, uow, id_generator, clock) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock

    async def execute(
        self,
        user_id: str,
        tag_id: str,
        name: str,
        category: str,
        notes: str | None,
    ) -> ItemsCreateResult:
        async with self._uow:
            tag = self._uow.tags.get(tag_id)
            if not tag:
                raise NotFoundError("tag not found")
            if tag.owner_id != user_id:
                raise AuthorizationError("tag does not belong to user")

            item_id = self._id_generator.new_id()
            item = Item(
                id=item_id,
                owner_id=user_id,
                tag_id=tag_id,
                name=name,
                category=category,
                notes=notes,
                created_at=self._clock.now(),
            )
            self._uow.items[item.id] = item
            await self._uow.commit()
            return ItemsCreateResult(item_id=item.id)
