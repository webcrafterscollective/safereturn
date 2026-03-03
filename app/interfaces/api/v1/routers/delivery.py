from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.application.use_cases.delivery_create_request import DeliveryCreateRequestUseCase
from app.application.use_cases.delivery_get_request import DeliveryGetRequestUseCase
from app.interfaces.api.v1.dependencies import AppContainer, get_container, get_current_user_id
from app.interfaces.api.v1.schemas.delivery import (
    DeliveryCreateRequest,
    DeliveryCreateResponse,
    DeliveryGetResponse,
)

router = APIRouter(prefix="/deliveries", tags=["delivery"])


@router.post("", response_model=DeliveryCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_request(
    request: DeliveryCreateRequest,
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> DeliveryCreateResponse:
    use_case = DeliveryCreateRequestUseCase(
        uow=container.new_uow(),
        id_generator=container.id_generator,
        clock=container.clock,
        delivery_provider=container.delivery_provider,
    )
    result = await use_case.execute(
        user_id=user_id,
        conversation_id=request.conversation_id,
        pickup_drop_details_stub=request.pickup_drop_details_stub,
    )
    return DeliveryCreateResponse(delivery_id=result.delivery_id, status=result.status)


@router.get("/{delivery_id}", response_model=DeliveryGetResponse)
async def get_delivery_request(
    delivery_id: str,
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> DeliveryGetResponse:
    _ = user_id
    use_case = DeliveryGetRequestUseCase(uow=container.new_uow())
    result = await use_case.execute(delivery_id=delivery_id)
    return DeliveryGetResponse(
        delivery_id=result.delivery_id,
        status=result.status,
        provider_ref=result.provider_ref,
    )
