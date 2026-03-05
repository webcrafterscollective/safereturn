"""Prometheus metrics endpoint."""

from fastapi import APIRouter, Response

from app.core.settings import get_settings
from app.metrics.prometheus import render_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics", summary="Prometheus metrics")
async def metrics() -> Response:
    """Expose Prometheus text format metrics when enabled."""
    settings = get_settings()
    if not settings.prometheus_enabled:
        return Response(status_code=404)

    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)
