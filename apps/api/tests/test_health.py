"""Integration tests for liveness and readiness endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_live(async_client) -> None:
    """Liveness endpoint must return 200 and live status."""
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "live"


@pytest.mark.asyncio
async def test_health_ready(async_client) -> None:
    """Readiness endpoint must return 200 when DB is reachable."""
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
