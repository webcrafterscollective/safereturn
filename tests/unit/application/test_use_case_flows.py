from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from app.application.use_cases.auth_login import AuthLoginUseCase
from app.application.use_cases.auth_register import AuthRegisterUseCase
from app.application.use_cases.delivery_create_request import DeliveryCreateRequestUseCase
from app.application.use_cases.items_create import ItemsCreateUseCase
from app.application.use_cases.items_mark_found import ItemsMarkFoundUseCase
from app.application.use_cases.items_mark_lost import ItemsMarkLostUseCase
from app.application.use_cases.owner_send_message import OwnerSendMessageUseCase
from app.application.use_cases.public_create_finder_session import PublicCreateFinderSessionUseCase
from app.application.use_cases.public_get_page import PublicGetPageUseCase
from app.application.use_cases.public_send_message import PublicSendMessageUseCase
from app.domain.entities.conversation import Conversation
from app.domain.entities.delivery_request import DeliveryRequest
from app.domain.entities.finder_session import FinderSession
from app.domain.entities.item import Item
from app.domain.entities.lost_report import LostReport
from app.domain.entities.message import Message
from app.domain.entities.tag import Tag
from app.domain.entities.user import User


class FakeClock:
    def now(self) -> datetime:
        return datetime(2026, 3, 4, tzinfo=UTC)


class FakeIdGen:
    def __init__(self) -> None:
        self.value = 0

    def new_id(self) -> str:
        self.value += 1
        return f"id_{self.value}"


class FakeEncryption:
    def encrypt(self, value: str) -> str:
        return f"enc::{value}"

    def decrypt(self, value: str) -> str:
        return value.replace("enc::", "", 1)


class FakeTokens:
    def issue_access_refresh(self, user_id: str) -> tuple[str, str, str]:
        return (f"access-{user_id}", f"refresh-{user_id}", f"hash-{user_id}")

    def verify_access(self, token: str) -> str:
        return token.removeprefix("access-")

    def rotate_refresh(self, refresh_token: str) -> tuple[str, str, str]:
        user_id = refresh_token.removeprefix("refresh-")
        return self.issue_access_refresh(user_id=user_id)


class FakeRateLimiter:
    def __init__(self) -> None:
        self.allowed = True

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        return self.allowed


class FakeNotifications:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def send(self, to_user_id: str, event_type: str, payload: dict[str, str]) -> None:
        self.calls.append((to_user_id, event_type))


class FakeDeliveryProvider:
    async def quote(self, payload: dict[str, str]) -> dict[str, str]:
        return {"amount": "100"}

    async def book(self, payload: dict[str, str]) -> dict[str, str]:
        return {"provider_ref": "booked-1", "status": "booked"}

    async def cancel(self, provider_ref: str) -> dict[str, str]:
        return {"status": "canceled"}

    async def track(self, provider_ref: str) -> dict[str, str]:
        return {"status": "booked"}


@dataclass
class FakeUow:
    users: dict[str, User]
    tags: dict[str, Tag]
    items: dict[str, Item]
    lost_reports: dict[str, LostReport]
    finder_sessions: dict[str, FinderSession]
    conversations: dict[str, Conversation]
    messages: dict[str, Message]
    deliveries: dict[str, DeliveryRequest]
    committed: bool = False

    async def __aenter__(self) -> FakeUow:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        if exc:
            self.committed = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False


@pytest.fixture
def uow() -> FakeUow:
    return FakeUow(
        users={},
        tags={
            "tag_1": Tag(
                id="tag_1",
                public_token="vQ6W2xkR3M7qYp8hNu4zDw",
                claim_code="CLAIM-001",
                status="unclaimed",
                owner_id=None,
                created_at=datetime(2026, 3, 4, tzinfo=UTC),
            )
        },
        items={},
        lost_reports={},
        finder_sessions={},
        conversations={},
        messages={},
        deliveries={},
    )


@pytest.mark.asyncio
async def test_register_login_claim_create_and_mark_lost_found(uow: FakeUow) -> None:
    clock = FakeClock()
    id_gen = FakeIdGen()
    encryptor = FakeEncryption()
    tokens = FakeTokens()

    register_use_case = AuthRegisterUseCase(
        uow=uow, id_generator=id_gen, clock=clock, encryption=encryptor
    )
    register_result = await register_use_case.execute(email="owner@example.com", phone=None)

    login_use_case = AuthLoginUseCase(uow=uow, token_service=tokens)
    login_result = await login_use_case.execute(
        email_or_phone="owner@example.com", otp_or_password_stub="123456"
    )

    assert register_result.user_id in uow.users
    assert login_result.access_token.startswith("access-")

    claimed_tag = uow.tags["tag_1"]
    claimed_tag.owner_id = register_result.user_id
    claimed_tag.status = "claimed"

    create_item = ItemsCreateUseCase(uow=uow, id_generator=id_gen, clock=clock)
    created = await create_item.execute(
        user_id=register_result.user_id,
        tag_id="tag_1",
        name="Laptop",
        category="electronics",
        notes="Blue sleeve",
    )

    mark_lost = ItemsMarkLostUseCase(uow=uow, id_generator=id_gen, clock=clock)
    lost_result = await mark_lost.execute(user_id=register_result.user_id, item_id=created.item_id)

    mark_found = ItemsMarkFoundUseCase(uow=uow, clock=clock)
    found_result = await mark_found.execute(
        user_id=register_result.user_id, item_id=created.item_id
    )

    assert lost_result.is_lost is True
    assert found_result.is_lost is False


@pytest.mark.asyncio
async def test_public_page_and_messaging_flow(uow: FakeUow) -> None:
    clock = FakeClock()
    id_gen = FakeIdGen()
    limiter = FakeRateLimiter()
    notifications = FakeNotifications()

    owner = User(
        id="owner_1",
        created_at=clock.now(),
        email_encrypted="enc::owner@example.com",
        phone_encrypted=None,
        email_verified=False,
        phone_verified=False,
        status="active",
        refresh_token_hash=None,
    )
    uow.users[owner.id] = owner

    tag = uow.tags["tag_1"]
    tag.owner_id = owner.id
    tag.status = "claimed"

    item = Item(
        id="item_1",
        owner_id=owner.id,
        tag_id=tag.id,
        name="Laptop",
        category="electronics",
        notes="Blue sleeve",
        created_at=clock.now(),
    )
    uow.items[item.id] = item
    uow.lost_reports[item.id] = LostReport(
        id="lr_1",
        item_id=item.id,
        is_lost=True,
        lost_at=clock.now(),
        found_at=None,
    )

    public_page = PublicGetPageUseCase(uow=uow)
    page = await public_page.execute(public_token=tag.public_token)
    assert "owner" not in page.safe_item_label.lower()

    create_session = PublicCreateFinderSessionUseCase(
        uow=uow,
        id_generator=id_gen,
        clock=clock,
        rate_limiter=limiter,
    )
    session = await create_session.execute(public_token=tag.public_token)

    send_message = PublicSendMessageUseCase(
        uow=uow,
        id_generator=id_gen,
        clock=clock,
        notifications=notifications,
        rate_limiter=limiter,
    )
    sent = await send_message.execute(
        public_token=tag.public_token,
        finder_session_token=session.finder_session_token,
        message_body="I found this near gate 3.",
    )

    owner_reply = OwnerSendMessageUseCase(uow=uow, id_generator=id_gen, clock=clock)
    owner_sent = await owner_reply.execute(
        user_id=owner.id,
        conversation_id=sent.conversation_id,
        message_body="Thanks, can we meet at 5 PM?",
    )

    assert owner_sent.message_id in uow.messages
    assert notifications.calls == [(owner.id, "finder_message_received")]


@pytest.mark.asyncio
async def test_delivery_request_is_booked_with_provider(uow: FakeUow) -> None:
    clock = FakeClock()
    id_gen = FakeIdGen()
    provider = FakeDeliveryProvider()

    owner = User(
        id="owner_1",
        created_at=clock.now(),
        email_encrypted="enc::owner@example.com",
        phone_encrypted=None,
        email_verified=False,
        phone_verified=False,
        status="active",
        refresh_token_hash=None,
    )
    uow.users[owner.id] = owner
    uow.conversations["conv_1"] = Conversation(
        id="conv_1",
        item_id="item_1",
        owner_id=owner.id,
        finder_anon_id="finder_1",
        status="open",
        created_at=clock.now(),
    )

    use_case = DeliveryCreateRequestUseCase(
        uow=uow,
        id_generator=id_gen,
        clock=clock,
        delivery_provider=provider,
    )
    result = await use_case.execute(
        user_id=owner.id,
        conversation_id="conv_1",
        pickup_drop_details_stub={"pickup": "A", "drop": "B"},
    )

    assert result.status == "booked"
    assert uow.deliveries[result.delivery_id].provider_ref == "booked-1"
