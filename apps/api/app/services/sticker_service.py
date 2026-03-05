"""Service layer for sticker packs, claim lifecycle, and admin operations."""

from datetime import UTC, datetime
from secrets import token_hex

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.item import Item
from app.models.qr_sticker import QRSticker
from app.models.sticker_pack import StickerPack
from app.models.user import User
from app.repositories.user_repo import UserRepository


class StickerService:
    """Business service for pack generation, claim lifecycle, and sticker maintenance."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    @staticmethod
    def _new_pack_code() -> str:
        """Return a human-readable pack code to print on physical sticker pack."""
        return f"PACK-{token_hex(4).upper()}"

    @staticmethod
    def _new_sticker_code() -> str:
        """Return a unique sticker code encoded in each sticker QR."""
        return f"SR-{token_hex(5).upper()}"

    async def generate_pack(
        self, *, admin_user_id: str, quantity: int
    ) -> tuple[StickerPack, list[QRSticker]]:
        """Create one sticker pack and its unclaimed sticker inventory."""
        if quantity < 1 or quantity > 500:
            raise AppError(
                code="INVALID_QUANTITY",
                message="Quantity must be between 1 and 500",
                status_code=422,
            )

        pack = StickerPack(
            pack_code=self._new_pack_code(),
            total_stickers=quantity,
            status="generated",
            created_by_user_id=admin_user_id,
        )
        self.session.add(pack)
        await self.session.flush()

        stickers: list[QRSticker] = []
        for _ in range(quantity):
            sticker = QRSticker(
                code=self._new_sticker_code(),
                owner_user_id=None,
                pack_id=pack.id,
                status="unassigned",
                assigned_once=False,
            )
            stickers.append(sticker)
            self.session.add(sticker)

        await self.session.commit()
        await self.session.refresh(pack)
        return pack, stickers

    async def list_packs(self) -> list[StickerPack]:
        """List packs newest-first for admin tracking."""
        result = await self.session.execute(
            select(StickerPack).order_by(StickerPack.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pack_stickers(self, *, pack_id: str) -> list[QRSticker]:
        """Return stickers belonging to one pack."""
        result = await self.session.execute(
            select(QRSticker)
            .where(QRSticker.pack_id == pack_id)
            .order_by(QRSticker.created_at.asc())
        )
        return list(result.scalars().all())

    async def claim_pack(self, *, user_id: str, pack_code: str) -> list[QRSticker]:
        """Claim pack for user and assign every active sticker in that pack."""
        result = await self.session.execute(
            select(StickerPack).where(StickerPack.pack_code == pack_code)
        )
        pack = result.scalar_one_or_none()
        if pack is None:
            raise AppError(code="PACK_NOT_FOUND", message="Sticker pack not found", status_code=404)

        if pack.assigned_user_id is not None and pack.assigned_user_id != user_id:
            raise AppError(
                code="PACK_ALREADY_CLAIMED",
                message="Pack is already claimed by another account",
                status_code=409,
            )

        stickers_result = await self.session.execute(
            select(QRSticker)
            .where(QRSticker.pack_id == pack.id)
            .order_by(QRSticker.created_at.asc())
        )
        stickers = list(stickers_result.scalars().all())
        if not stickers:
            raise AppError(
                code="PACK_EMPTY",
                message="Sticker pack has no stickers",
                status_code=409,
            )

        now = datetime.now(UTC)
        for sticker in stickers:
            if sticker.invalidated_at is None:
                sticker.owner_user_id = user_id
                sticker.claimed_at = now

        pack.assigned_user_id = user_id
        pack.claimed_at = now
        pack.status = "claimed"

        await self.session.commit()
        return stickers

    async def create_user_and_assign_pack(
        self, *, email: str, password: str, pack_code: str | None
    ) -> tuple[str, str, str | None]:
        """Admin workflow to provision owner account and optionally claim a pack."""
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise AppError(
                code="EMAIL_ALREADY_EXISTS",
                message="An account with this email already exists",
                status_code=409,
            )

        user = await self.user_repo.create_user_with_role(
            email=email,
            password_hash=hash_password(password),
            is_admin=False,
        )
        assigned_pack_code: str | None = None
        if pack_code is not None and pack_code.strip():
            cleaned_pack_code = pack_code.strip()
            await self.claim_pack(user_id=user.id, pack_code=cleaned_pack_code)
            assigned_pack_code = cleaned_pack_code
        return user.id, user.email, assigned_pack_code

    async def list_user_stickers(self, *, user_id: str) -> list[QRSticker]:
        """List all stickers currently owned by user."""
        result = await self.session.execute(
            select(QRSticker)
            .where(QRSticker.owner_user_id == user_id)
            .order_by(QRSticker.created_at.asc())
        )
        return list(result.scalars().all())

    async def list_owner_items(self, *, user_id: str) -> list[tuple[Item, QRSticker | None]]:
        """List owner items with optional linked sticker for dashboard tracking."""
        items_result = await self.session.execute(
            select(Item).where(Item.owner_user_id == user_id).order_by(Item.created_at.desc())
        )
        items = list(items_result.scalars().all())
        output: list[tuple[Item, QRSticker | None]] = []
        for item in items:
            sticker_result = await self.session.execute(
                select(QRSticker).where(QRSticker.item_id == item.id).limit(1)
            )
            sticker = sticker_result.scalar_one_or_none()
            output.append((item, sticker))
        return output

    async def regenerate_sticker(self, *, user_id: str, sticker_code: str) -> QRSticker:
        """Replace one unbound sticker code with a fresh code for same owner."""
        result = await self.session.execute(select(QRSticker).where(QRSticker.code == sticker_code))
        sticker = result.scalar_one_or_none()
        if sticker is None or sticker.owner_user_id != user_id:
            raise AppError(code="STICKER_NOT_FOUND", message="Sticker not found", status_code=404)
        if sticker.assigned_once or sticker.item_id is not None:
            raise AppError(
                code="STICKER_ALREADY_BOUND",
                message="Bound stickers cannot be regenerated",
                status_code=409,
            )
        if sticker.invalidated_at is not None:
            raise AppError(
                code="STICKER_ALREADY_INVALIDATED",
                message="Sticker is already invalidated",
                status_code=409,
            )

        replacement_code = self._new_sticker_code()
        now = datetime.now(UTC)
        sticker.invalidated_at = now
        sticker.status = "disabled"
        sticker.replaced_by_code = replacement_code

        replacement = QRSticker(
            code=replacement_code,
            owner_user_id=user_id,
            pack_id=sticker.pack_id,
            status="unassigned",
            assigned_once=False,
            claimed_at=sticker.claimed_at or now,
        )
        self.session.add(replacement)
        await self.session.commit()
        await self.session.refresh(replacement)
        return replacement

    async def invalidate_sticker(self, *, user_id: str, sticker_code: str) -> None:
        """Disable one sticker permanently before it is linked to an item."""
        result = await self.session.execute(select(QRSticker).where(QRSticker.code == sticker_code))
        sticker = result.scalar_one_or_none()
        if sticker is None or sticker.owner_user_id != user_id:
            raise AppError(code="STICKER_NOT_FOUND", message="Sticker not found", status_code=404)
        if sticker.assigned_once or sticker.item_id is not None:
            raise AppError(
                code="STICKER_ALREADY_BOUND",
                message="Bound stickers cannot be invalidated",
                status_code=409,
            )
        if sticker.invalidated_at is not None:
            return
        sticker.invalidated_at = datetime.now(UTC)
        sticker.status = "disabled"
        await self.session.commit()

    async def mark_item_found(self, *, user_id: str, item_id: str) -> None:
        """Mark item as found and update linked sticker status."""
        item_result = await self.session.execute(
            select(Item).where(Item.id == item_id, Item.owner_user_id == user_id)
        )
        item = item_result.scalar_one_or_none()
        if item is None:
            raise AppError(code="ITEM_NOT_FOUND", message="Item not found", status_code=404)

        item.is_lost = False
        sticker_result = await self.session.execute(
            select(QRSticker).where(QRSticker.item_id == item_id)
        )
        sticker = sticker_result.scalar_one_or_none()
        if sticker is not None:
            sticker.status = "recovered"
        await self.session.commit()

    async def report_claim_issue(
        self, *, sticker_code: str, reporter_user_id: str | None, note: str
    ) -> int:
        """Record support ticket trail for already-claimed/invalid sticker issues."""
        event = AuditLog(
            user_id=reporter_user_id,
            event_type="sticker_claim_issue",
            event_data=f'{{"sticker_code":"{sticker_code}","note":"{note}"}}',
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event.id

    async def admin_overview(self) -> dict[str, int]:
        """Return aggregate counters for admin dashboard cards."""
        counts = {
            "users": await self.session.scalar(select(func.count()).select_from(User)),
            "packs": await self.session.scalar(select(func.count()).select_from(StickerPack)),
            "stickers": await self.session.scalar(select(func.count()).select_from(QRSticker)),
            "claimed_packs": await self.session.scalar(
                select(func.count()).select_from(StickerPack).where(StickerPack.status == "claimed")
            ),
            "unassigned_stickers": await self.session.scalar(
                select(func.count())
                .select_from(QRSticker)
                .where(QRSticker.status == "unassigned", QRSticker.invalidated_at.is_(None))
            ),
        }
        return {key: int(value or 0) for key, value in counts.items()}
