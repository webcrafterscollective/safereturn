from __future__ import annotations

from pydantic import BaseModel, Field


class PublicPageResponse(BaseModel):
    safe_item_label: str
    is_lost: bool
    instructions: str


class PublicCreateSessionResponse(BaseModel):
    finder_session_token: str
    expires_at: str


class PublicSendMessageRequest(BaseModel):
    finder_session_token: str
    message_body: str = Field(min_length=1, max_length=500)


class PublicSendMessageResponse(BaseModel):
    conversation_id: str
    message_id: str


class PublicMessageItemResponse(BaseModel):
    message_id: str
    sender_type: str
    body: str


class PublicMessagesResponse(BaseModel):
    messages: list[PublicMessageItemResponse]
