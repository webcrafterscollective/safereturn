"""Integration tests for Prometheus metrics endpoint exposure."""

import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint(async_client) -> None:
    """Metrics endpoint should return Prometheus-formatted payload."""
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests_total" in response.text
