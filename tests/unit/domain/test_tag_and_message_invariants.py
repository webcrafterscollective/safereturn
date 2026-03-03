from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.entities.finder_session import FinderSession
from app.domain.entities.message import Message
from app.domain.entities.tag import Tag
from app.domain.errors import InvariantViolationError


def test_tag_rejects_low_entropy_public_token() -> None:
    with pytest.raises(InvariantViolationError, match="public token"):
        Tag(
            id="tag_1",
            public_token="short-token",
            claim_code="CLAIM-001",
            status="claimed",
            owner_id="user_1",
            created_at=datetime.now(tz=UTC),
        )


def test_tag_accepts_high_entropy_public_token() -> None:
    token = "vQ6W2xkR3M7qYp8hNu4zDw"  # 22+ base64url chars ~= 128 bits
    tag = Tag(
        id="tag_1",
        public_token=token,
        claim_code="CLAIM-001",
        status="unclaimed",
        owner_id=None,
        created_at=datetime.now(tz=UTC),
    )

    assert tag.public_token == token


def test_message_rejects_blank_and_oversized_body() -> None:
    with pytest.raises(InvariantViolationError, match="message body"):
        Message.create(
            id="msg_1",
            conversation_id="conv_1",
            sender_type="finder",
            body="   ",
            created_at=datetime.now(tz=UTC),
        )

    with pytest.raises(InvariantViolationError, match="message body"):
        Message.create(
            id="msg_2",
            conversation_id="conv_1",
            sender_type="owner",
            body="x" * 501,
            created_at=datetime.now(tz=UTC),
        )


def test_message_applies_basic_anti_abuse_rule() -> None:
    with pytest.raises(InvariantViolationError, match="repeated characters"):
        Message.create(
            id="msg_3",
            conversation_id="conv_1",
            sender_type="finder",
            body="!!!!!!!!!!!!!!!",
            created_at=datetime.now(tz=UTC),
        )


def test_finder_session_expiry_must_be_in_future() -> None:
    now = datetime.now(tz=UTC)
    with pytest.raises(InvariantViolationError, match="expiry"):
        FinderSession(
            id="fs_1",
            public_token="vQ6W2xkR3M7qYp8hNu4zDw",
            session_token="opaque-session-token",
            expires_at=now - timedelta(seconds=1),
            created_at=now,
        )
