"""Admin API endpoints for sticker-pack inventory and provisioning workflows."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_session
from app.models.qr_sticker import QRSticker
from app.models.sticker_pack import StickerPack
from app.routers.deps.auth import require_admin_user_id
from app.schemas.admin import (
    AdminOverviewResponse,
    CreateUserAndAssignPackRequest,
    CreateUserAndAssignPackResponse,
    GeneratePackRequest,
    GeneratePackResponse,
    ListPacksResponse,
    PackStickersResponse,
    StickerPackSummary,
)
from app.schemas.recovery import StickerSummary
from app.services.sticker_service import StickerService

router = APIRouter(prefix="/admin", tags=["admin"])


def _to_pack_summary(pack: StickerPack) -> StickerPackSummary:
    """Map sticker pack ORM model to API response schema."""
    return StickerPackSummary(
        id=pack.id,
        pack_code=pack.pack_code,
        total_stickers=pack.total_stickers,
        status=pack.status,
        assigned_user_id=pack.assigned_user_id,
        created_at=pack.created_at,
        claimed_at=pack.claimed_at,
    )


def _to_sticker_summary(sticker: QRSticker, request: Request) -> StickerSummary:
    """Map sticker ORM model to dashboard-friendly response payload."""
    scan_url = str(request.url_for("spa_fallback", full_path="scan"))
    return StickerSummary(
        code=sticker.code,
        status=sticker.status,
        item_id=sticker.item_id,
        assigned_once=sticker.assigned_once,
        claimed_at=sticker.claimed_at,
        invalidated_at=sticker.invalidated_at,
        replaced_by_code=sticker.replaced_by_code,
        qr_scan_url=f"{scan_url}?code={sticker.code}",
    )


@router.get("/overview", response_model=AdminOverviewResponse, status_code=status.HTTP_200_OK)
async def overview(
    _: str = Depends(require_admin_user_id),
    session: AsyncSession = Depends(get_session),
) -> AdminOverviewResponse:
    """Return key counters for the admin portal dashboard."""
    service = StickerService(session)
    summary = await service.admin_overview()
    return AdminOverviewResponse(**summary)


@router.post(
    "/packs/generate",
    response_model=GeneratePackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_pack(
    payload: GeneratePackRequest,
    request: Request,
    admin_user_id: str = Depends(require_admin_user_id),
    session: AsyncSession = Depends(get_session),
) -> GeneratePackResponse:
    """Generate a new sticker pack and return all printable sticker codes."""
    service = StickerService(session)
    pack, stickers = await service.generate_pack(
        admin_user_id=admin_user_id,
        quantity=payload.quantity,
    )
    return GeneratePackResponse(
        pack=_to_pack_summary(pack),
        stickers=[_to_sticker_summary(sticker, request) for sticker in stickers],
    )


@router.get("/packs", response_model=ListPacksResponse, status_code=status.HTTP_200_OK)
async def list_packs(
    _: str = Depends(require_admin_user_id),
    session: AsyncSession = Depends(get_session),
) -> ListPacksResponse:
    """List sticker packs for tracking generated/claimed inventory."""
    service = StickerService(session)
    packs = await service.list_packs()
    return ListPacksResponse(packs=[_to_pack_summary(pack) for pack in packs])


@router.get(
    "/packs/{pack_id}/stickers",
    response_model=PackStickersResponse,
    status_code=status.HTTP_200_OK,
)
async def list_pack_stickers(
    pack_id: str,
    request: Request,
    _: str = Depends(require_admin_user_id),
    session: AsyncSession = Depends(get_session),
) -> PackStickersResponse:
    """List sticker codes for one selected pack."""
    service = StickerService(session)
    packs = await service.list_packs()
    selected_pack = next((pack for pack in packs if pack.id == pack_id), None)
    if selected_pack is None:
        raise AppError(code="PACK_NOT_FOUND", message="Sticker pack not found", status_code=404)

    stickers = await service.get_pack_stickers(pack_id=pack_id)
    return PackStickersResponse(
        pack=_to_pack_summary(selected_pack),
        stickers=[_to_sticker_summary(sticker, request) for sticker in stickers],
    )


@router.post(
    "/users/create-and-assign-pack",
    response_model=CreateUserAndAssignPackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_and_assign_pack(
    payload: CreateUserAndAssignPackRequest,
    _: str = Depends(require_admin_user_id),
    session: AsyncSession = Depends(get_session),
) -> CreateUserAndAssignPackResponse:
    """Create owner account and optionally assign/claim a sticker pack to that account."""
    service = StickerService(session)
    user_id, email, assigned_pack_code = await service.create_user_and_assign_pack(
        email=payload.email,
        password=payload.password,
        pack_code=payload.pack_code,
    )
    return CreateUserAndAssignPackResponse(
        user_id=user_id,
        email=email,
        assigned_pack_code=assigned_pack_code,
    )
