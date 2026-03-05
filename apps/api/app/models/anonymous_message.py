"""Anonymous relay message ORM model for finder-owner communications."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnonymousMessage(Base):
    """Stored message exchanged in a finder session without exposing identities."""

    __tablename__ = "anonymous_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    finder_session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("finder_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_role: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True
    )
