from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import AuthorizationError, NotFoundError
from app.domain.entities.lost_report import LostReport


@dataclass(slots=True)
class ItemsMarkLostResult:
    is_lost: bool


class ItemsMarkLostUseCase:
    def __init__(self, uow, id_generator, clock) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock

    async def execute(self, user_id: str, item_id: str) -> ItemsMarkLostResult:
        async with self._uow:
            item = self._uow.items.get(item_id)
            if not item:
                raise NotFoundError("item not found")
            if item.owner_id != user_id:
                raise AuthorizationError("item does not belong to user")

            report = self._uow.lost_reports.get(item_id)
            if report is None:
                report = LostReport(
                    id=self._id_generator.new_id(),
                    item_id=item_id,
                    is_lost=True,
                    lost_at=self._clock.now(),
                    found_at=None,
                )
                self._uow.lost_reports[item_id] = report
            else:
                report.is_lost = True
                report.found_at = None

            await self._uow.commit()
            return ItemsMarkLostResult(is_lost=True)
