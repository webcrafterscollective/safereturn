from __future__ import annotations

from fastapi import APIRouter, Depends, Header, status

from app.application.errors import AuthorizationError
from app.application.use_cases.admin_batch_create_tags import AdminBatchCreateTagsUseCase
from app.interfaces.api.v1.dependencies import AppContainer, get_container
from app.interfaces.api.v1.schemas.admin import (
    AdminBatchCreateTagsRequest,
    AdminBatchCreateTagsResponse,
    AdminTagItemResponse,
)
from app.settings import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/tags/batch-create",
    response_model=AdminBatchCreateTagsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def batch_create_tags(
    request: AdminBatchCreateTagsRequest,
    container: AppContainer = Depends(get_container),
    x_admin_api_key: str | None = Header(default=None),
) -> AdminBatchCreateTagsResponse:
    if x_admin_api_key != get_settings().admin_api_key:
        raise AuthorizationError("invalid admin api key")

    use_case = AdminBatchCreateTagsUseCase(
        uow=container.new_uow(),
        id_generator=container.id_generator,
        clock=container.clock,
        token_factory=container.tag_token_factory,
    )
    result = await use_case.execute(count=request.count)
    return AdminBatchCreateTagsResponse(
        tags=[
            AdminTagItemResponse(
                tag_id=item.tag_id,
                claim_code=item.claim_code,
                public_token=item.public_token,
            )
            for item in result.tags
        ]
    )
