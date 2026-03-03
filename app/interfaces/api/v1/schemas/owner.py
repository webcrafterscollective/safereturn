from __future__ import annotations

from pydantic import BaseModel, Field


class TagsClaimRequest(BaseModel):
    claim_code: str


class TagsClaimResponse(BaseModel):
    tag_id: str
    public_token: str


class ItemsCreateRequest(BaseModel):
    tag_id: str
    name: str
    category: str
    notes: str | None = None


class ItemIdResponse(BaseModel):
    item_id: str


class LostStatusResponse(BaseModel):
    is_lost: bool


class ItemListItemResponse(BaseModel):
    item_id: str
    tag_id: str
    name: str
    category: str
    notes: str | None
    is_lost: bool


class ItemsListResponse(BaseModel):
    items: list[ItemListItemResponse]


class OwnerConversationItemResponse(BaseModel):
    conversation_id: str
    item_id: str
    status: str


class OwnerConversationsResponse(BaseModel):
    conversations: list[OwnerConversationItemResponse]


class OwnerSendMessageRequest(BaseModel):
    message_body: str = Field(min_length=1, max_length=500)


class MessageIdResponse(BaseModel):
    message_id: str
