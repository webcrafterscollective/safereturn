"""Sticker pack inventory entity."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.errors import InvariantViolationError


@dataclass(slots=True)
class StickerPack:
    id: str
    pack_code: str
    quantity: int
    status: str
    issued_to: str | None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvariantViolationError("sticker pack quantity must be positive")
        if self.status not in {"created", "issued", "disabled"}:
            raise InvariantViolationError("invalid sticker pack status")
