"""Health endpoints for liveness and readiness checks."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Liveness probe")
async def health_live() -> dict[str, str]:
    """Return process liveness status."""
    return {"status": "live"}


@router.get("/health/ready", summary="Readiness probe")
async def health_ready(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """Return readiness status after checking database connectivity."""
    await session.execute(text("SELECT 1"))
    return {"status": "ready"}
