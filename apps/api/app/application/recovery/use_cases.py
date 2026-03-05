"""Recovery use cases orchestrating QR workflows through dependency-inverted ports."""

from collections.abc import Sequence

from app.application.recovery.dtos import (
    FinderSessionDTO,
    LostReportDTO,
    MarkItemLostCommand,
    RegisteredStickerDTO,
    RegisterStickerCommand,
    RelayMessageCommand,
    RelayMessageDTO,
    StartFinderSessionCommand,
)
from app.application.recovery.ports import NotificationPort, RecoveryRepositoryPort
from app.domain.recovery.entities import LostReportStatus, SenderRole, StickerStatus
from app.domain.recovery.services import (
    compute_session_expiry,
    generate_public_session_token,
    hash_public_session_token,
    is_session_expired,
)


class RecoveryUseCaseError(Exception):
    """Application-layer exception mapped to API error responses by routers."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class RecoveryUseCases:
    """Business workflows for item registration, scanning, and anonymous messaging."""

    def __init__(
        self,
        *,
        repository: RecoveryRepositoryPort,
        notifier: NotificationPort,
        secret_key: str,
        finder_session_ttl_minutes: int,
    ) -> None:
        self.repository = repository
        self.notifier = notifier
        self.secret_key = secret_key
        self.finder_session_ttl_minutes = finder_session_ttl_minutes

    async def register_sticker(self, *, command: RegisterStickerCommand) -> RegisteredStickerDTO:
        """Attach a claimed sticker to a newly created owner item."""
        existing = await self.repository.get_sticker_by_code(code=command.sticker_code)
        if existing is None:
            raise RecoveryUseCaseError(
                code="STICKER_NOT_FOUND",
                message="Sticker code not found. Use a valid platform-issued sticker.",
                status_code=404,
            )
        if existing.owner_user_id is None:
            raise RecoveryUseCaseError(
                code="STICKER_UNCLAIMED",
                message="Sticker is not claimed yet. Claim your sticker pack first.",
                status_code=409,
            )
        if existing.owner_user_id != command.owner_user_id:
            raise RecoveryUseCaseError(
                code="FORBIDDEN",
                message="Sticker belongs to another account.",
                status_code=403,
            )
        if existing.assigned_once or existing.item_id is not None:
            raise RecoveryUseCaseError(
                code="STICKER_ALREADY_USED",
                message="Sticker can only be assigned once and is already linked.",
                status_code=409,
            )
        if existing.status == StickerStatus.DISABLED:
            raise RecoveryUseCaseError(
                code="STICKER_DISABLED",
                message="Sticker is disabled and cannot be used.",
                status_code=409,
            )

        item = await self.repository.create_item_for_owner(
            owner_user_id=command.owner_user_id,
            display_name=command.item_name,
            category=command.item_category,
            description=command.item_description,
        )

        sticker = await self.repository.attach_sticker_to_item(
            sticker_code=command.sticker_code,
            owner_user_id=command.owner_user_id,
            item_id=item.id,
        )
        if sticker is None:
            raise RecoveryUseCaseError(
                code="STICKER_ASSIGNMENT_FAILED",
                message="Sticker could not be attached to this item.",
                status_code=409,
            )

        return RegisteredStickerDTO(
            item_id=item.id,
            sticker_code=sticker.code,
            status=sticker.status.value,
        )

    async def mark_item_lost(self, *, command: MarkItemLostCommand) -> LostReportDTO:
        """Mark owner item as lost and open a report for support/analytics."""
        item = await self.repository.set_item_lost_state(
            owner_user_id=command.owner_user_id,
            item_id=command.item_id,
            is_lost=True,
        )
        if item is None:
            raise RecoveryUseCaseError(
                code="ITEM_NOT_FOUND",
                message="Item not found for this owner",
                status_code=404,
            )

        report = await self.repository.create_lost_report(
            owner_user_id=command.owner_user_id,
            item_id=command.item_id,
            status=LostReportStatus.OPEN.value,
            last_known_location=command.last_known_location,
            notes=command.notes,
        )

        sticker = await self.repository.get_sticker_by_item_id(item_id=command.item_id)
        if sticker is not None:
            await self.repository.set_sticker_status(
                sticker_id=sticker.id, status=StickerStatus.LOST
            )

        return LostReportDTO(
            report_id=report.id,
            item_id=report.item_id,
            status=report.status.value,
            created_at=report.created_at,
        )

    async def start_finder_session(self, *, command: StartFinderSessionCommand) -> FinderSessionDTO:
        """Create an expiring finder session from scanned sticker code."""
        sticker = await self.repository.get_sticker_by_code(code=command.sticker_code)
        if sticker is None:
            raise RecoveryUseCaseError(
                code="STICKER_NOT_FOUND",
                message="Sticker not found",
                status_code=404,
            )
        if sticker.owner_user_id is None:
            raise RecoveryUseCaseError(
                code="STICKER_UNCLAIMED",
                message="Sticker belongs to an unclaimed pack. Please register and claim it.",
                status_code=409,
            )
        if sticker.item_id is None:
            raise RecoveryUseCaseError(
                code="STICKER_UNREGISTERED",
                message="Sticker is claimed but not yet linked to an item.",
                status_code=409,
            )
        if sticker.status == StickerStatus.DISABLED:
            raise RecoveryUseCaseError(
                code="STICKER_DISABLED",
                message="Sticker is disabled",
                status_code=410,
            )

        expires_at = compute_session_expiry(ttl_minutes=self.finder_session_ttl_minutes)
        public_token = generate_public_session_token()
        token_hash = hash_public_session_token(token=public_token, secret_key=self.secret_key)

        session = await self.repository.create_finder_session(
            sticker_id=sticker.id,
            public_token_hash=token_hash,
            expires_at=expires_at,
            finder_note=command.finder_note,
        )

        item = await self.repository.get_item_for_session(finder_session_id=session.id)
        item_name = item.display_name if item is not None else "Registered item"

        await self.notifier.notify_owner_lost_item_scanned(
            owner_user_id=sticker.owner_user_id,
            item_name=item_name,
            finder_note=command.finder_note,
        )

        return FinderSessionDTO(
            session_token=public_token,
            item_name=item_name,
            owner_hint="Owner contact is protected. Send a message and they will be notified.",
            expires_at=session.expires_at,
        )

    async def relay_message(self, *, command: RelayMessageCommand) -> RelayMessageDTO:
        """Store and relay anonymous message from finder or owner."""
        token_hash = hash_public_session_token(
            token=command.session_token, secret_key=self.secret_key
        )
        session = await self.repository.get_finder_session_by_token_hash(token_hash=token_hash)
        if session is None:
            raise RecoveryUseCaseError(
                code="SESSION_NOT_FOUND",
                message="Finder session is invalid",
                status_code=404,
            )

        if is_session_expired(expires_at=session.expires_at):
            raise RecoveryUseCaseError(
                code="SESSION_EXPIRED",
                message="Finder session has expired",
                status_code=410,
            )

        if command.sender_role is SenderRole.OWNER and command.owner_user_id is not None:
            owner_allowed = await self.repository.verify_owner_can_access_session(
                owner_user_id=command.owner_user_id,
                finder_session_id=session.id,
            )
            if not owner_allowed:
                raise RecoveryUseCaseError(
                    code="FORBIDDEN",
                    message="Owner cannot access this session",
                    status_code=403,
                )

        message = await self.repository.create_anonymous_message(
            finder_session_id=session.id,
            sender_role=command.sender_role,
            body=command.message_body,
        )

        if command.sender_role is SenderRole.FINDER:
            item = await self.repository.get_item_for_session(finder_session_id=session.id)
            owner_user_id = item.owner_user_id if item is not None else None
            if owner_user_id is not None:
                await self.notifier.notify_owner_new_message(
                    owner_user_id=owner_user_id,
                    message_preview=command.message_body[:80],
                )

        return RelayMessageDTO(
            session_reference=session.id,
            sender_role=message.sender_role,
            body=message.body,
            created_at=message.created_at,
        )

    async def list_owner_messages(self, *, owner_user_id: str) -> Sequence[RelayMessageDTO]:
        """Return owner inbox messages across active finder sessions."""
        messages = await self.repository.list_owner_messages(owner_user_id=owner_user_id)
        results: list[RelayMessageDTO] = []
        for message in messages:
            results.append(
                RelayMessageDTO(
                    session_reference=message.finder_session_id,
                    sender_role=message.sender_role,
                    body=message.body,
                    created_at=message.created_at,
                )
            )
        return results

    async def relay_owner_message(
        self, *, owner_user_id: str, session_reference: str, message_body: str
    ) -> RelayMessageDTO:
        """Store owner reply using internal session reference from owner inbox."""
        session = await self.repository.get_finder_session_by_id(
            finder_session_id=session_reference
        )
        if session is None:
            raise RecoveryUseCaseError(
                code="SESSION_NOT_FOUND",
                message="Finder session is invalid",
                status_code=404,
            )

        if is_session_expired(expires_at=session.expires_at):
            raise RecoveryUseCaseError(
                code="SESSION_EXPIRED",
                message="Finder session has expired",
                status_code=410,
            )

        owner_allowed = await self.repository.verify_owner_can_access_session(
            owner_user_id=owner_user_id,
            finder_session_id=session.id,
        )
        if not owner_allowed:
            raise RecoveryUseCaseError(
                code="FORBIDDEN",
                message="Owner cannot access this session",
                status_code=403,
            )

        message = await self.repository.create_anonymous_message(
            finder_session_id=session.id,
            sender_role=SenderRole.OWNER,
            body=message_body,
        )
        return RelayMessageDTO(
            session_reference=session.id,
            sender_role=message.sender_role,
            body=message.body,
            created_at=message.created_at,
        )
