from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from app.application.errors import RateLimitExceededError
from app.application.use_cases._helpers import find_tag_by_public_token
from app.domain.entities.finder_session import FinderSession


@dataclass(slots=True)
class PublicCreateFinderSessionResult:
    finder_session_token: str
    expires_at: str


class PublicCreateFinderSessionUseCase:
    def __init__(self, uow, id_generator, clock, rate_limiter) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock
        self._rate_limiter = rate_limiter

    async def execute(self, public_token: str) -> PublicCreateFinderSessionResult:
        key = f"scan:{public_token}"
        if not self._rate_limiter.allow(key=key, limit=15, window_seconds=60):
            raise RateLimitExceededError("scan rate limit exceeded")

        async with self._uow:
            tag = find_tag_by_public_token(self._uow.tags, public_token)
            now = self._clock.now()
            expires_at = now + timedelta(minutes=30)
            session_token = f"session::{self._id_generator.new_id()}"
            session = FinderSession(
                id=self._id_generator.new_id(),
                public_token=tag.public_token,
                session_token=session_token,
                created_at=now,
                expires_at=expires_at,
            )
            self._uow.finder_sessions[session_token] = session
            await self._uow.commit()
            return PublicCreateFinderSessionResult(
                finder_session_token=session_token,
                expires_at=expires_at.isoformat(),
            )
