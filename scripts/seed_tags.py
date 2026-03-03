"""Seed script to generate unclaimed tags for sticker printing."""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime

from sqlalchemy import insert

from app.infrastructure.db.models import TagModel
from app.infrastructure.db.session import create_engine
from app.infrastructure.idgen.uuid_id_generator import UuidIdGenerator
from app.infrastructure.security.tag_token_factory import TagTokenFactory
from app.settings import get_settings


async def seed_tags(count: int) -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    factory = TagTokenFactory()
    id_generator = UuidIdGenerator()

    rows = [
        {
            "id": id_generator.new_id(),
            "public_token": factory.new_public_token(),
            "claim_code": factory.new_claim_code(),
            "status": "unclaimed",
            "owner_id": None,
            "created_at": datetime.now(tz=UTC),
        }
        for _ in range(count)
    ]

    async with engine.begin() as conn:
        await conn.execute(insert(TagModel), rows)

    await engine.dispose()

    for row in rows:
        print(f"{row['claim_code']},{row['public_token']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed QR tags")
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()
    asyncio.run(seed_tags(count=args.count))


if __name__ == "__main__":
    main()
