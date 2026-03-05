"""QR sticker ORM model used for scan resolution and item binding."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QRSticker(Base):
    """Physical QR sticker linked to an owner item."""

    __tablename__ = "qr_stickers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    owner_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    pack_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("sticker_packs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="unassigned", index=True
    )
    assigned_once: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
