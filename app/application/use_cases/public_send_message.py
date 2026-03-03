from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import AuthorizationError, NotFoundError, RateLimitExceededError
from app.application.use_cases._helpers import find_tag_by_public_token
from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message


@dataclass(slots=True)
class PublicSendMessageResult:
    conversation_id: str
    message_id: str


class PublicSendMessageUseCase:
    def __init__(self, uow, id_generator, clock, notifications, rate_limiter) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock
        self._notifications = notifications
        self._rate_limiter = rate_limiter

    async def execute(
        self,
        public_token: str,
        finder_session_token: str,
        message_body: str,
    ) -> PublicSendMessageResult:
        limiter_key = f"message:{public_token}:{finder_session_token}"
        if not self._rate_limiter.allow(key=limiter_key, limit=20, window_seconds=60):
            raise RateLimitExceededError("message rate limit exceeded")

        async with self._uow:
            tag = find_tag_by_public_token(self._uow.tags, public_token)
            if tag.owner_id is None:
                raise NotFoundError("tag not claimed")

            session = self._uow.finder_sessions.get(finder_session_token)
            if not session:
                raise AuthorizationError("invalid finder session")
            if session.public_token != public_token:
                raise AuthorizationError("finder session does not match tag")
            if session.expires_at <= self._clock.now():
                raise AuthorizationError("finder session expired")

            item = next((it for it in self._uow.items.values() if it.tag_id == tag.id), None)
            if item is None:
                raise NotFoundError("item not found")

            conversation = next(
                (
                    conv
                    for conv in self._uow.conversations.values()
                    if conv.item_id == item.id and conv.finder_anon_id == session.id
                ),
                None,
            )
            if conversation is None:
                conversation = Conversation(
                    id=self._id_generator.new_id(),
                    item_id=item.id,
                    owner_id=item.owner_id,
                    finder_anon_id=session.id,
                    status="open",
                    created_at=self._clock.now(),
                )
                self._uow.conversations[conversation.id] = conversation

            message = Message.create(
                id=self._id_generator.new_id(),
                conversation_id=conversation.id,
                sender_type="finder",
                body=message_body,
                created_at=self._clock.now(),
            )
            self._uow.messages[message.id] = message
            await self._notifications.send(
                to_user_id=conversation.owner_id,
                event_type="finder_message_received",
                payload={"conversation_id": conversation.id},
            )
            await self._uow.commit()
            return PublicSendMessageResult(
                conversation_id=conversation.id,
                message_id=message.id,
            )
