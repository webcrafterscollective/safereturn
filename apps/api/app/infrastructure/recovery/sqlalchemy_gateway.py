"""SQLAlchemy adapter implementing recovery repository port methods."""

from datetime import UTC, datetime

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.recovery.ports import RecoveryRepositoryPort
from app.domain.recovery.entities import (
    AnonymousMessage,
    FinderSession,
    Item,
    LostItemReport,
    LostReportStatus,
    QRSticker,
    SenderRole,
    StickerStatus,
)
from app.models.anonymous_message import AnonymousMessage as AnonymousMessageModel
from app.models.finder_session import FinderSession as FinderSessionModel
from app.models.item import Item as ItemModel
from app.models.lost_item_report import LostItemReport as LostItemReportModel
from app.models.qr_sticker import QRSticker as QRStickerModel


class SqlAlchemyRecoveryRepository(RecoveryRepositoryPort):
    """Persistence adapter for recovery use cases using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_sticker_by_code(self, *, code: str) -> QRSticker | None:
        stmt: Select[tuple[QRStickerModel]] = select(QRStickerModel).where(
            QRStickerModel.code == code
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_sticker(model) if model is not None else None

    async def get_sticker_by_item_id(self, *, item_id: str) -> QRSticker | None:
        stmt: Select[tuple[QRStickerModel]] = select(QRStickerModel).where(
            QRStickerModel.item_id == item_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_sticker(model) if model is not None else None

    async def create_item_for_owner(
        self,
        *,
        owner_user_id: str,
        display_name: str,
        category: str,
        description: str,
    ) -> Item:
        model = ItemModel(
            owner_user_id=owner_user_id,
            display_name=display_name,
            category=category,
            description=description,
            is_lost=False,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_item(model)

    async def create_sticker_for_owner(
        self,
        *,
        owner_user_id: str,
        code: str,
        item_id: str,
        status: StickerStatus,
    ) -> QRSticker:
        model = QRStickerModel(
            owner_user_id=owner_user_id,
            code=code,
            item_id=item_id,
            status=status.value,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_sticker(model)

    async def set_item_lost_state(
        self, *, owner_user_id: str, item_id: str, is_lost: bool
    ) -> Item | None:
        stmt: Select[tuple[ItemModel]] = select(ItemModel).where(
            ItemModel.id == item_id,
            ItemModel.owner_user_id == owner_user_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        model.is_lost = is_lost
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_item(model)

    async def create_lost_report(
        self,
        *,
        owner_user_id: str,
        item_id: str,
        status: str,
        last_known_location: str | None,
        notes: str | None,
    ) -> LostItemReport:
        model = LostItemReportModel(
            owner_user_id=owner_user_id,
            item_id=item_id,
            status=status,
            last_known_location=last_known_location,
            notes=notes,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_lost_report(model)

    async def set_sticker_status(self, *, sticker_id: str, status: StickerStatus) -> None:
        stmt: Select[tuple[QRStickerModel]] = select(QRStickerModel).where(
            QRStickerModel.id == sticker_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return
        model.status = status.value
        await self.session.commit()

    async def create_finder_session(
        self,
        *,
        sticker_id: str,
        public_token_hash: str,
        expires_at: datetime,
        finder_note: str | None,
    ) -> FinderSession:
        model = FinderSessionModel(
            sticker_id=sticker_id,
            public_token_hash=public_token_hash,
            expires_at=expires_at,
            finder_note=finder_note,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_finder_session(model)

    async def get_finder_session_by_token_hash(self, *, token_hash: str) -> FinderSession | None:
        stmt: Select[tuple[FinderSessionModel]] = select(FinderSessionModel).where(
            FinderSessionModel.public_token_hash == token_hash,
            FinderSessionModel.closed_at.is_(None),
            FinderSessionModel.expires_at > self._utc_now(),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_finder_session(model) if model is not None else None

    async def get_finder_session_by_id(self, *, finder_session_id: str) -> FinderSession | None:
        stmt: Select[tuple[FinderSessionModel]] = select(FinderSessionModel).where(
            FinderSessionModel.id == finder_session_id,
            FinderSessionModel.closed_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_finder_session(model) if model is not None else None

    async def get_item_for_session(self, *, finder_session_id: str) -> Item | None:
        stmt = (
            select(ItemModel)
            .join(QRStickerModel, QRStickerModel.item_id == ItemModel.id)
            .join(FinderSessionModel, FinderSessionModel.sticker_id == QRStickerModel.id)
            .where(FinderSessionModel.id == finder_session_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_item(model) if model is not None else None

    async def create_anonymous_message(
        self,
        *,
        finder_session_id: str,
        sender_role: SenderRole,
        body: str,
    ) -> AnonymousMessage:
        model = AnonymousMessageModel(
            finder_session_id=finder_session_id,
            sender_role=sender_role.value,
            body=body,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_message(model)

    async def list_owner_messages(self, *, owner_user_id: str) -> list[AnonymousMessage]:
        stmt = (
            select(AnonymousMessageModel)
            .join(
                FinderSessionModel, FinderSessionModel.id == AnonymousMessageModel.finder_session_id
            )
            .join(QRStickerModel, QRStickerModel.id == FinderSessionModel.sticker_id)
            .join(ItemModel, ItemModel.id == QRStickerModel.item_id)
            .where(ItemModel.owner_user_id == owner_user_id)
            .order_by(AnonymousMessageModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_message(model) for model in result.scalars().all()]

    async def verify_owner_can_access_session(
        self, *, owner_user_id: str, finder_session_id: str
    ) -> bool:
        stmt = (
            select(FinderSessionModel.id)
            .join(QRStickerModel, QRStickerModel.id == FinderSessionModel.sticker_id)
            .join(ItemModel, ItemModel.id == QRStickerModel.item_id)
            .where(
                FinderSessionModel.id == finder_session_id,
                ItemModel.owner_user_id == owner_user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def _to_item(model: ItemModel) -> Item:
        return Item(
            id=model.id,
            owner_user_id=model.owner_user_id,
            display_name=model.display_name,
            category=model.category,
            description=model.description,
            is_lost=model.is_lost,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_sticker(model: QRStickerModel) -> QRSticker:
        return QRSticker(
            id=model.id,
            code=model.code,
            owner_user_id=model.owner_user_id,
            item_id=model.item_id,
            status=StickerStatus(model.status),
            created_at=model.created_at,
        )

    @staticmethod
    def _to_finder_session(model: FinderSessionModel) -> FinderSession:
        return FinderSession(
            id=model.id,
            sticker_id=model.sticker_id,
            public_token=model.public_token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            finder_note=model.finder_note,
        )

    @staticmethod
    def _to_message(model: AnonymousMessageModel) -> AnonymousMessage:
        return AnonymousMessage(
            id=model.id,
            finder_session_id=model.finder_session_id,
            sender_role=SenderRole(model.sender_role),
            body=model.body,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_lost_report(model: LostItemReportModel) -> LostItemReport:
        return LostItemReport(
            id=model.id,
            item_id=model.item_id,
            owner_user_id=model.owner_user_id,
            status=LostReportStatus(model.status),
            last_known_location=model.last_known_location,
            notes=model.notes,
            created_at=model.created_at,
        )
