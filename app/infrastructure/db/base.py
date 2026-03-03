"""Database declarative base."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models for side-effect registration in metadata.
from app.infrastructure.db import models as _models  # noqa: F401,E402
