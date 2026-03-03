"""Shared in-memory state for local/dev and tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities.conversation import Conversation
from app.domain.entities.delivery_request import DeliveryRequest
from app.domain.entities.finder_session import FinderSession
from app.domain.entities.item import Item
from app.domain.entities.lost_report import LostReport
from app.domain.entities.message import Message
from app.domain.entities.tag import Tag
from app.domain.entities.user import User


@dataclass(slots=True)
class InMemoryState:
    users: dict[str, User] = field(default_factory=dict)
    tags: dict[str, Tag] = field(default_factory=dict)
    items: dict[str, Item] = field(default_factory=dict)
    lost_reports: dict[str, LostReport] = field(default_factory=dict)
    finder_sessions: dict[str, FinderSession] = field(default_factory=dict)
    conversations: dict[str, Conversation] = field(default_factory=dict)
    messages: dict[str, Message] = field(default_factory=dict)
    deliveries: dict[str, DeliveryRequest] = field(default_factory=dict)


class InMemoryUnitOfWork:
    def __init__(self, state: InMemoryState) -> None:
        self._state = state
        self.users = state.users
        self.tags = state.tags
        self.items = state.items
        self.lost_reports = state.lost_reports
        self.finder_sessions = state.finder_sessions
        self.conversations = state.conversations
        self.messages = state.messages
        self.deliveries = state.deliveries

    async def __aenter__(self) -> InMemoryUnitOfWork:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        if exc:
            await self.rollback()

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None
