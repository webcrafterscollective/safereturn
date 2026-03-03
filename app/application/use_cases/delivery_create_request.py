from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import AuthorizationError, NotFoundError
from app.domain.entities.delivery_request import DeliveryRequest


@dataclass(slots=True)
class DeliveryCreateRequestResult:
    delivery_id: str
    status: str


class DeliveryCreateRequestUseCase:
    def __init__(self, uow, id_generator, clock, delivery_provider) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock
        self._delivery_provider = delivery_provider

    async def execute(
        self,
        user_id: str,
        conversation_id: str,
        pickup_drop_details_stub: dict[str, str],
    ) -> DeliveryCreateRequestResult:
        async with self._uow:
            conversation = self._uow.conversations.get(conversation_id)
            if not conversation:
                raise NotFoundError("conversation not found")
            if conversation.owner_id != user_id:
                raise AuthorizationError("conversation does not belong to user")

            provider_response = await self._delivery_provider.book(pickup_drop_details_stub)
            delivery = DeliveryRequest(
                id=self._id_generator.new_id(),
                conversation_id=conversation_id,
                status=provider_response.get("status", "booked"),
                provider="mock_delivery",
                provider_ref=provider_response.get("provider_ref"),
                created_at=self._clock.now(),
            )
            self._uow.deliveries[delivery.id] = delivery
            await self._uow.commit()
            return DeliveryCreateRequestResult(delivery_id=delivery.id, status=delivery.status)
