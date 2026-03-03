from __future__ import annotations

from pydantic import BaseModel


class DeliveryCreateRequest(BaseModel):
    conversation_id: str
    pickup_drop_details_stub: dict[str, str]


class DeliveryCreateResponse(BaseModel):
    delivery_id: str
    status: str


class DeliveryGetResponse(BaseModel):
    delivery_id: str
    status: str
    provider_ref: str | None
