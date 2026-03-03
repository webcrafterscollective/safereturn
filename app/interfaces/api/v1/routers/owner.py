from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.application.use_cases.items_create import ItemsCreateUseCase
from app.application.use_cases.items_list import ItemsListUseCase
from app.application.use_cases.items_mark_found import ItemsMarkFoundUseCase
from app.application.use_cases.items_mark_lost import ItemsMarkLostUseCase
from app.application.use_cases.owner_list_conversations import OwnerListConversationsUseCase
from app.application.use_cases.owner_send_message import OwnerSendMessageUseCase
from app.application.use_cases.tags_claim import TagsClaimUseCase
from app.interfaces.api.v1.dependencies import AppContainer, get_container, get_current_user_id
from app.interfaces.api.v1.schemas.owner import (
    ItemIdResponse,
    ItemListItemResponse,
    ItemsCreateRequest,
    ItemsListResponse,
    LostStatusResponse,
    MessageIdResponse,
    OwnerConversationItemResponse,
    OwnerConversationsResponse,
    OwnerSendMessageRequest,
    TagsClaimRequest,
    TagsClaimResponse,
)

router = APIRouter(tags=["owner"])


@router.post("/tags/claim", response_model=TagsClaimResponse)
async def claim_tag(
    request: TagsClaimRequest,
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> TagsClaimResponse:
    use_case = TagsClaimUseCase(uow=container.new_uow())
    result = await use_case.execute(user_id=user_id, claim_code=request.claim_code)
    return TagsClaimResponse(tag_id=result.tag_id, public_token=result.public_token)


@router.post("/items", response_model=ItemIdResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    request: ItemsCreateRequest,
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> ItemIdResponse:
    use_case = ItemsCreateUseCase(
        uow=container.new_uow(),
        id_generator=container.id_generator,
        clock=container.clock,
    )
    result = await use_case.execute(
        user_id=user_id,
        tag_id=request.tag_id,
        name=request.name,
        category=request.category,
        notes=request.notes,
    )
    return ItemIdResponse(item_id=result.item_id)


@router.get("/items", response_model=ItemsListResponse)
async def list_items(
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> ItemsListResponse:
    use_case = ItemsListUseCase(uow=container.new_uow())
    result = await use_case.execute(user_id=user_id)
    return ItemsListResponse(
        items=[
            ItemListItemResponse(
                item_id=item.item_id,
                tag_id=item.tag_id,
                name=item.name,
                category=item.category,
                notes=item.notes,
                is_lost=item.is_lost,
            )
            for item in result.items
        ]
    )


@router.post("/items/{item_id}/lost", response_model=LostStatusResponse)
async def mark_item_lost(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> LostStatusResponse:
    use_case = ItemsMarkLostUseCase(
        uow=container.new_uow(),
        id_generator=container.id_generator,
        clock=container.clock,
    )
    result = await use_case.execute(user_id=user_id, item_id=item_id)
    return LostStatusResponse(is_lost=result.is_lost)


@router.post("/items/{item_id}/found", response_model=LostStatusResponse)
async def mark_item_found(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> LostStatusResponse:
    use_case = ItemsMarkFoundUseCase(uow=container.new_uow(), clock=container.clock)
    result = await use_case.execute(user_id=user_id, item_id=item_id)
    return LostStatusResponse(is_lost=result.is_lost)


@router.get("/conversations", response_model=OwnerConversationsResponse)
async def list_owner_conversations(
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> OwnerConversationsResponse:
    use_case = OwnerListConversationsUseCase(uow=container.new_uow())
    result = await use_case.execute(user_id=user_id)
    return OwnerConversationsResponse(
        conversations=[
            OwnerConversationItemResponse(
                conversation_id=item.conversation_id,
                item_id=item.item_id,
                status=item.status,
            )
            for item in result.conversations
        ]
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageIdResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_owner_message(
    conversation_id: str,
    request: OwnerSendMessageRequest,
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> MessageIdResponse:
    use_case = OwnerSendMessageUseCase(
        uow=container.new_uow(),
        id_generator=container.id_generator,
        clock=container.clock,
    )
    result = await use_case.execute(
        user_id=user_id,
        conversation_id=conversation_id,
        message_body=request.message_body,
    )
    return MessageIdResponse(message_id=result.message_id)
