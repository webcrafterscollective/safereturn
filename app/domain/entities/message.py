"""Secure conversation message entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errors import InvariantViolationError

_MAX_BODY_LENGTH = 500
_MAX_REPEATED_CHAR = 12


@dataclass(slots=True)
class Message:
    id: str
    conversation_id: str
    sender_type: str
    body: str
    created_at: datetime

    @classmethod
    def create(
        cls,
        id: str,
        conversation_id: str,
        sender_type: str,
        body: str,
        created_at: datetime,
    ) -> Message:
        normalized_body = body.strip()
        if not normalized_body or len(normalized_body) > _MAX_BODY_LENGTH:
            raise InvariantViolationError("message body must be between 1 and 500 chars")
        if _has_excessive_repeated_characters(normalized_body):
            raise InvariantViolationError("message body contains repeated characters")
        if sender_type not in {"owner", "finder"}:
            raise InvariantViolationError("sender type is invalid")
        return cls(
            id=id,
            conversation_id=conversation_id,
            sender_type=sender_type,
            body=normalized_body,
            created_at=created_at,
        )


def _has_excessive_repeated_characters(body: str) -> bool:
    current_char = ""
    run_length = 0
    for char in body:
        if char == current_char:
            run_length += 1
        else:
            current_char = char
            run_length = 1
        if run_length >= _MAX_REPEATED_CHAR:
            return True
    return False
