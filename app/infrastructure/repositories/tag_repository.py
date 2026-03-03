"""SQLAlchemy tag repository adapter."""

from __future__ import annotations

from sqlalchemy import select

from app.domain.entities.tag import Tag
from app.infrastructure.db.models import TagModel


class SqlAlchemyTagRepository:
    def __init__(self, session) -> None:  # type: ignore[no-untyped-def]
        self._session = session

    async def add(self, tag: Tag) -> None:
        self._session.add(
            TagModel(
                id=tag.id,
                public_token=tag.public_token,
                claim_code=tag.claim_code,
                status=tag.status,
                owner_id=tag.owner_id,
                created_at=tag.created_at,
            )
        )

    async def get_by_public_token(self, public_token: str) -> Tag | None:
        statement = select(TagModel).where(TagModel.public_token == public_token)
        model = (await self._session.execute(statement)).scalar_one_or_none()
        if not model:
            return None
        return Tag(
            id=model.id,
            public_token=model.public_token,
            claim_code=model.claim_code,
            status=model.status,
            owner_id=model.owner_id,
            created_at=model.created_at,
        )
