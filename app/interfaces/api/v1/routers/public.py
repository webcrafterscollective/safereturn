from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.application.use_cases.finder_get_messages import FinderGetMessagesUseCase
from app.application.use_cases.public_create_finder_session import PublicCreateFinderSessionUseCase
from app.application.use_cases.public_get_page import PublicGetPageUseCase
from app.application.use_cases.public_send_message import PublicSendMessageUseCase
from app.interfaces.api.v1.dependencies import AppContainer, get_container
from app.interfaces.api.v1.schemas.public import (
    PublicCreateSessionResponse,
    PublicMessageItemResponse,
    PublicMessagesResponse,
    PublicPageResponse,
    PublicSendMessageRequest,
    PublicSendMessageResponse,
)

router = APIRouter(prefix="/p", tags=["public"])


@router.get("/{public_token}", response_model=PublicPageResponse)
async def get_public_page(
    public_token: str,
    container: AppContainer = Depends(get_container),
) -> PublicPageResponse:
    use_case = PublicGetPageUseCase(uow=container.new_uow())
    result = await use_case.execute(public_token=public_token)
    return PublicPageResponse(
        safe_item_label=result.safe_item_label,
        is_lost=result.is_lost,
        instructions=result.instructions,
    )


@router.post(
    "/{public_token}/sessions",
    response_model=PublicCreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_finder_session(
    public_token: str,
    container: AppContainer = Depends(get_container),
) -> PublicCreateSessionResponse:
    use_case = PublicCreateFinderSessionUseCase(
        uow=container.new_uow(),
        id_generator=container.id_generator,
        clock=container.clock,
        rate_limiter=container.rate_limiter,
    )
    result = await use_case.execute(public_token=public_token)
    return PublicCreateSessionResponse(
        finder_session_token=result.finder_session_token,
        expires_at=result.expires_at,
    )


@router.post(
    "/{public_token}/message",
    response_model=PublicSendMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_public_message(
    public_token: str,
    request: PublicSendMessageRequest,
    container: AppContainer = Depends(get_container),
) -> PublicSendMessageResponse:
    use_case = PublicSendMessageUseCase(
        uow=container.new_uow(),
        id_generator=container.id_generator,
        clock=container.clock,
        notifications=container.notifications,
        rate_limiter=container.rate_limiter,
    )
    result = await use_case.execute(
        public_token=public_token,
        finder_session_token=request.finder_session_token,
        message_body=request.message_body,
    )
    return PublicSendMessageResponse(
        conversation_id=result.conversation_id,
        message_id=result.message_id,
    )


@router.get("/{public_token}/messages", response_model=PublicMessagesResponse)
async def get_public_messages(
    public_token: str,
    finder_session_token: str,
    container: AppContainer = Depends(get_container),
) -> PublicMessagesResponse:
    use_case = FinderGetMessagesUseCase(uow=container.new_uow(), clock=container.clock)
    result = await use_case.execute(
        public_token=public_token,
        finder_session_token=finder_session_token,
    )
    return PublicMessagesResponse(
        messages=[
            PublicMessageItemResponse(
                message_id=item.message_id,
                sender_type=item.sender_type,
                body=item.body,
            )
            for item in result.messages
        ]
    )
