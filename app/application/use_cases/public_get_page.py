from __future__ import annotations

from dataclasses import dataclass

from app.application.use_cases._helpers import find_tag_by_public_token


@dataclass(slots=True)
class PublicPageResult:
    safe_item_label: str
    is_lost: bool
    instructions: str


class PublicGetPageUseCase:
    def __init__(self, uow) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow

    async def execute(self, public_token: str) -> PublicPageResult:
        async with self._uow:
            tag = find_tag_by_public_token(self._uow.tags, public_token)
            item = next((it for it in self._uow.items.values() if it.tag_id == tag.id), None)
            if item is None:
                label = "Registered item"
                is_lost = False
            else:
                report = self._uow.lost_reports.get(item.id)
                is_lost = bool(report and report.is_lost)
                label = f"{item.category.title()} item"

            return PublicPageResult(
                safe_item_label=label,
                is_lost=is_lost,
                instructions="Use this page to contact the owner securely.",
            )
