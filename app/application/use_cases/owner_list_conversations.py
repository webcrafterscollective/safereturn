from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConversationListItem:
    conversation_id: str
    item_id: str
    status: str


@dataclass(slots=True)
class OwnerListConversationsResult:
    conversations: list[ConversationListItem]


class OwnerListConversationsUseCase:
    def __init__(self, uow) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow

    async def execute(self, user_id: str) -> OwnerListConversationsResult:
        async with self._uow:
            conversations = [
                ConversationListItem(
                    conversation_id=conv.id,
                    item_id=conv.item_id,
                    status=conv.status,
                )
                for conv in self._uow.conversations.values()
                if conv.owner_id == user_id
            ]
            return OwnerListConversationsResult(conversations=conversations)
