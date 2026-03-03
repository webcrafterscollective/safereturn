from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import NotFoundError


@dataclass(slots=True)
class DeliveryGetRequestResult:
    delivery_id: str
    status: str
    provider_ref: str | None


class DeliveryGetRequestUseCase:
    def __init__(self, uow) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow

    async def execute(self, delivery_id: str) -> DeliveryGetRequestResult:
        async with self._uow:
            delivery = self._uow.deliveries.get(delivery_id)
            if not delivery:
                raise NotFoundError("delivery request not found")
            return DeliveryGetRequestResult(
                delivery_id=delivery.id,
                status=delivery.status,
                provider_ref=delivery.provider_ref,
            )
