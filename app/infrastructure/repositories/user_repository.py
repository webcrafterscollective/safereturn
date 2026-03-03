"""SQLAlchemy user repository adapter."""

from __future__ import annotations

from app.domain.entities.user import User
from app.infrastructure.db.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session) -> None:  # type: ignore[no-untyped-def]
        self._session = session

    async def add(self, user: User) -> None:
        self._session.add(
            UserModel(
                id=user.id,
                created_at=user.created_at,
                email_encrypted=user.email_encrypted,
                phone_encrypted=user.phone_encrypted,
                email_verified=user.email_verified,
                phone_verified=user.phone_verified,
                status=user.status,
                refresh_token_hash=user.refresh_token_hash,
            )
        )

    async def get_by_id(self, user_id: str) -> User | None:
        model = await self._session.get(UserModel, user_id)
        if not model:
            return None
        return User(
            id=model.id,
            created_at=model.created_at,
            email_encrypted=model.email_encrypted,
            phone_encrypted=model.phone_encrypted,
            email_verified=model.email_verified,
            phone_verified=model.phone_verified,
            status=model.status,
            refresh_token_hash=model.refresh_token_hash,
        )
