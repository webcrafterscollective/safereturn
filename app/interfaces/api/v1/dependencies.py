"""Dependency wiring for API layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.errors import AuthorizationError
from app.infrastructure.clock.system_clock import SystemClock
from app.infrastructure.delivery.mock_provider import MockDeliveryProvider
from app.infrastructure.idgen.uuid_id_generator import UuidIdGenerator
from app.infrastructure.notifications.mock_notifications import MockNotificationAdapter
from app.infrastructure.repositories.in_memory_store import InMemoryState, InMemoryUnitOfWork
from app.infrastructure.security.encryption import FernetEncryptionAdapter
from app.infrastructure.security.rate_limiter import InMemoryRateLimiter
from app.infrastructure.security.tag_token_factory import TagTokenFactory
from app.infrastructure.security.token_service import JwtTokenService
from app.settings import get_settings


@dataclass(slots=True)
class AppContainer:
    state: InMemoryState
    clock: SystemClock
    id_generator: UuidIdGenerator
    encryption: FernetEncryptionAdapter
    token_service: JwtTokenService
    rate_limiter: InMemoryRateLimiter
    notifications: MockNotificationAdapter
    delivery_provider: MockDeliveryProvider
    tag_token_factory: TagTokenFactory

    def new_uow(self) -> InMemoryUnitOfWork:
        return InMemoryUnitOfWork(self.state)


_http_bearer = HTTPBearer(auto_error=False)


def build_container() -> AppContainer:
    settings = get_settings()
    return AppContainer(
        state=InMemoryState(),
        clock=SystemClock(),
        id_generator=UuidIdGenerator(),
        encryption=FernetEncryptionAdapter(settings.fernet_key),
        token_service=JwtTokenService(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_exp_minutes=settings.access_token_exp_minutes,
            refresh_token_exp_minutes=settings.refresh_token_exp_minutes,
        ),
        rate_limiter=InMemoryRateLimiter(),
        notifications=MockNotificationAdapter(),
        delivery_provider=MockDeliveryProvider(),
        tag_token_factory=TagTokenFactory(),
    )


def get_container(request: Request) -> AppContainer:
    return cast(AppContainer, request.app.state.container)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_http_bearer),
    container: AppContainer = Depends(get_container),
) -> str:
    if not credentials:
        raise AuthorizationError("missing bearer token")
    return container.token_service.verify_access(credentials.credentials)
