from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ItemListItem:
    item_id: str
    tag_id: str
    name: str
    category: str
    notes: str | None
    is_lost: bool


@dataclass(slots=True)
class ItemsListResult:
    items: list[ItemListItem]


class ItemsListUseCase:
    def __init__(self, uow) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow

    async def execute(self, user_id: str) -> ItemsListResult:
        async with self._uow:
            output: list[ItemListItem] = []
            for item in self._uow.items.values():
                if item.owner_id != user_id:
                    continue
                report = self._uow.lost_reports.get(item.id)
                output.append(
                    ItemListItem(
                        item_id=item.id,
                        tag_id=item.tag_id,
                        name=item.name,
                        category=item.category,
                        notes=item.notes,
                        is_lost=bool(report and report.is_lost),
                    )
                )
            return ItemsListResult(items=output)
