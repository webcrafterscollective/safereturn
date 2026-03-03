from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import AuthorizationError


@dataclass(slots=True)
class FinderMessageItem:
    message_id: str
    sender_type: str
    body: str


@dataclass(slots=True)
class FinderGetMessagesResult:
    messages: list[FinderMessageItem]


class FinderGetMessagesUseCase:
    def __init__(self, uow, clock) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._clock = clock

    async def execute(
        self, public_token: str, finder_session_token: str
    ) -> FinderGetMessagesResult:
        async with self._uow:
            session = self._uow.finder_sessions.get(finder_session_token)
            if not session:
                raise AuthorizationError("invalid finder session")
            if session.public_token != public_token:
                raise AuthorizationError("finder session does not match tag")
            if session.expires_at <= self._clock.now():
                raise AuthorizationError("finder session expired")

            conversation = next(
                (
                    conv
                    for conv in self._uow.conversations.values()
                    if conv.finder_anon_id == session.id
                ),
                None,
            )
            if conversation is None:
                return FinderGetMessagesResult(messages=[])

            messages = [
                FinderMessageItem(
                    message_id=msg.id,
                    sender_type=msg.sender_type,
                    body=msg.body,
                )
                for msg in self._uow.messages.values()
                if msg.conversation_id == conversation.id
            ]
            messages.sort(key=lambda message: message.message_id)
            return FinderGetMessagesResult(messages=messages)
