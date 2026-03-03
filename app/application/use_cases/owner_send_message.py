from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import AuthorizationError, NotFoundError
from app.domain.entities.message import Message


@dataclass(slots=True)
class OwnerSendMessageResult:
    message_id: str


class OwnerSendMessageUseCase:
    def __init__(self, uow, id_generator, clock) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock

    async def execute(
        self,
        user_id: str,
        conversation_id: str,
        message_body: str,
    ) -> OwnerSendMessageResult:
        async with self._uow:
            conversation = self._uow.conversations.get(conversation_id)
            if not conversation:
                raise NotFoundError("conversation not found")
            if conversation.owner_id != user_id:
                raise AuthorizationError("conversation does not belong to user")

            message = Message.create(
                id=self._id_generator.new_id(),
                conversation_id=conversation_id,
                sender_type="owner",
                body=message_body,
                created_at=self._clock.now(),
            )
            self._uow.messages[message.id] = message
            await self._uow.commit()
            return OwnerSendMessageResult(message_id=message.id)
