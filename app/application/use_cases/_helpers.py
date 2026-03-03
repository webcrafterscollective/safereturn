from __future__ import annotations

from app.application.errors import NotFoundError
from app.domain.entities.tag import Tag


def find_tag_by_public_token(tags: dict[str, Tag], public_token: str) -> Tag:
    for tag in tags.values():
        if tag.public_token == public_token:
            return tag
    raise NotFoundError("tag not found")
