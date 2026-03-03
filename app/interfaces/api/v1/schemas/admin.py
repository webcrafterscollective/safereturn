from __future__ import annotations

from pydantic import BaseModel, Field


class AdminBatchCreateTagsRequest(BaseModel):
    count: int = Field(ge=1, le=1000)


class AdminTagItemResponse(BaseModel):
    tag_id: str
    claim_code: str
    public_token: str


class AdminBatchCreateTagsResponse(BaseModel):
    tags: list[AdminTagItemResponse]
