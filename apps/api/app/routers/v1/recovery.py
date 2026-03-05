"""Recovery API endpoints for sticker registration, scan, and anonymous messaging."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.recovery.dtos import (
    MarkItemLostCommand,
    RegisterStickerCommand,
    RelayMessageCommand,
    StartFinderSessionCommand,
)
from app.application.recovery.use_cases import RecoveryUseCaseError, RecoveryUseCases
from app.core.errors import AppError
from app.core.settings import get_settings
from app.db.session import get_session
from app.domain.recovery.entities import SenderRole
from app.infrastructure.recovery.notifier import LoggingNotificationAdapter
from app.infrastructure.recovery.sqlalchemy_gateway import SqlAlchemyRecoveryRepository
from app.routers.deps.auth import get_current_user_id
from app.schemas.recovery import (
    LostReportResponse,
    MarkItemLostRequest,
    OwnerInboxResponse,
    RegisterStickerRequest,
    RegisterStickerResponse,
    RelayMessageRequest,
    RelayMessageResponse,
    ScanStickerRequest,
    ScanStickerResponse,
)

router = APIRouter(prefix="/recovery", tags=["recovery"])


def _build_use_cases(session: AsyncSession) -> RecoveryUseCases:
    """Create use-case service with infrastructure adapters for current request."""
    settings = get_settings()
    return RecoveryUseCases(
        repository=SqlAlchemyRecoveryRepository(session),
        notifier=LoggingNotificationAdapter(),
        secret_key=settings.secret_key,
        finder_session_ttl_minutes=settings.finder_session_ttl_minutes,
    )


def _raise_api_error(exc: RecoveryUseCaseError) -> None:
    """Translate application-layer exception into standardized API error."""
    raise AppError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc


@router.post(
    "/stickers/register",
    response_model=RegisterStickerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_sticker(
    payload: RegisterStickerRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> RegisterStickerResponse:
    """Register sticker and attach it to a newly created owner item."""
    use_cases = _build_use_cases(session)
    try:
        result = await use_cases.register_sticker(
            command=RegisterStickerCommand(
                owner_user_id=user_id,
                sticker_code=payload.sticker_code,
                item_name=payload.item_name,
                item_category=payload.item_category,
                item_description=payload.item_description,
            )
        )
    except RecoveryUseCaseError as exc:
        _raise_api_error(exc)

    return RegisterStickerResponse(
        item_id=result.item_id,
        sticker_code=result.sticker_code,
        status=result.status,
    )


@router.post(
    "/items/{item_id}/mark-lost",
    response_model=LostReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def mark_item_lost(
    item_id: str,
    payload: MarkItemLostRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> LostReportResponse:
    """Open lost-item report and set item status to lost."""
    use_cases = _build_use_cases(session)
    try:
        result = await use_cases.mark_item_lost(
            command=MarkItemLostCommand(
                owner_user_id=user_id,
                item_id=item_id,
                last_known_location=payload.last_known_location,
                notes=payload.notes,
            )
        )
    except RecoveryUseCaseError as exc:
        _raise_api_error(exc)

    return LostReportResponse(
        report_id=result.report_id,
        item_id=result.item_id,
        status=result.status,
        created_at=result.created_at,
    )


@router.post("/scan", response_model=ScanStickerResponse, status_code=status.HTTP_200_OK)
async def scan_sticker(
    payload: ScanStickerRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ScanStickerResponse:
    """Start a temporary finder session from scanned sticker code."""
    use_cases = _build_use_cases(session)
    try:
        result = await use_cases.start_finder_session(
            command=StartFinderSessionCommand(
                sticker_code=payload.sticker_code,
                finder_note=payload.finder_note,
                finder_ip=request.client.host if request.client is not None else None,
            )
        )
    except RecoveryUseCaseError as exc:
        _raise_api_error(exc)

    return ScanStickerResponse(
        session_token=result.session_token,
        item_name=result.item_name,
        owner_hint=result.owner_hint,
        expires_at=result.expires_at,
    )


@router.post(
    "/sessions/{session_token}/messages",
    response_model=RelayMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_finder_message(
    session_token: str,
    payload: RelayMessageRequest,
    session: AsyncSession = Depends(get_session),
) -> RelayMessageResponse:
    """Send anonymous finder message to owner relay inbox."""
    use_cases = _build_use_cases(session)
    try:
        result = await use_cases.relay_message(
            command=RelayMessageCommand(
                session_token=session_token,
                sender_role=SenderRole.FINDER,
                message_body=payload.message_body,
            )
        )
    except RecoveryUseCaseError as exc:
        _raise_api_error(exc)

    return RelayMessageResponse(
        session_reference=result.session_reference,
        sender_role=result.sender_role.value,
        body=result.body,
        created_at=result.created_at,
    )


@router.get("/owner/messages", response_model=OwnerInboxResponse, status_code=status.HTTP_200_OK)
async def list_owner_messages(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> OwnerInboxResponse:
    """List owner-facing anonymous messages across all items."""
    use_cases = _build_use_cases(session)
    messages = await use_cases.list_owner_messages(owner_user_id=user_id)
    return OwnerInboxResponse(
        messages=[
            RelayMessageResponse(
                session_reference=message.session_reference,
                sender_role=message.sender_role.value,
                body=message.body,
                created_at=message.created_at,
            )
            for message in messages
        ]
    )


@router.post(
    "/owner/sessions/{session_reference}/messages",
    response_model=RelayMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_owner_message(
    session_reference: str,
    payload: RelayMessageRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> RelayMessageResponse:
    """Send owner-side anonymous reply into finder relay thread."""
    use_cases = _build_use_cases(session)
    try:
        result = await use_cases.relay_owner_message(
            owner_user_id=user_id,
            session_reference=session_reference,
            message_body=payload.message_body,
        )
    except RecoveryUseCaseError as exc:
        _raise_api_error(exc)

    return RelayMessageResponse(
        session_reference=result.session_reference,
        sender_role=result.sender_role.value,
        body=result.body,
        created_at=result.created_at,
    )
