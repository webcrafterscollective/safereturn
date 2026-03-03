from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import AuthorizationError, NotFoundError


@dataclass(slots=True)
class ItemsMarkFoundResult:
    is_lost: bool


class ItemsMarkFoundUseCase:
    def __init__(self, uow, clock) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._clock = clock

    async def execute(self, user_id: str, item_id: str) -> ItemsMarkFoundResult:
        async with self._uow:
            item = self._uow.items.get(item_id)
            if not item:
                raise NotFoundError("item not found")
            if item.owner_id != user_id:
                raise AuthorizationError("item does not belong to user")

            report = self._uow.lost_reports.get(item_id)
            if not report:
                raise NotFoundError("lost report not found")
            report.is_lost = False
            report.found_at = self._clock.now()
            await self._uow.commit()
            return ItemsMarkFoundResult(is_lost=False)
