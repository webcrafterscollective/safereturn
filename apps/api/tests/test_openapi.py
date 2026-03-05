"""Integration tests for OpenAPI and Swagger docs path contract."""

import pytest


@pytest.mark.asyncio
async def test_openapi_json(async_client) -> None:
    """OpenAPI document must be available at /openapi.json."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["openapi"].startswith("3.")


@pytest.mark.asyncio
async def test_openapi_includes_all_documented_endpoints(async_client) -> None:
    """OpenAPI paths should expose all public API endpoints."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    payload = response.json()
    expected_paths = {
        "/api/v1/admin/overview",
        "/api/v1/admin/packs/generate",
        "/api/v1/admin/packs",
        "/api/v1/admin/packs/{pack_id}/stickers",
        "/api/v1/admin/users/create-and-assign-pack",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/auth/logout",
        "/api/v1/recovery/packs/claim",
        "/api/v1/recovery/stickers/mine",
        "/api/v1/recovery/stickers/{sticker_code}/regenerate",
        "/api/v1/recovery/stickers/{sticker_code}/invalidate",
        "/api/v1/recovery/stickers/register",
        "/api/v1/recovery/items/mine",
        "/api/v1/recovery/items/{item_id}/mark-lost",
        "/api/v1/recovery/items/{item_id}/mark-found",
        "/api/v1/recovery/scan",
        "/api/v1/recovery/claim-issues",
        "/api/v1/recovery/sessions/{session_token}/messages",
        "/api/v1/recovery/owner/messages",
        "/api/v1/recovery/owner/sessions/{session_reference}/messages",
        "/health/live",
        "/health/ready",
        "/metrics",
    }
    assert expected_paths.issubset(set(payload["paths"].keys()))


@pytest.mark.asyncio
async def test_swagger_ui_at_doc(async_client) -> None:
    """Swagger UI HTML should be served at /doc with same-origin assets only."""
    response = await async_client.get("/doc")
    assert response.status_code == 200
    assert "Swagger UI" in response.text
    assert "/swagger-assets/swagger-ui-bundle.js" in response.text
    assert "/swagger-assets/swagger-ui.css" in response.text
    assert "cdn.jsdelivr.net" not in response.text
    assert "fastapi.tiangolo.com" not in response.text


@pytest.mark.asyncio
async def test_docs_backward_compat_redirect(async_client) -> None:
    """Legacy /docs should redirect to the canonical /doc endpoint."""
    response = await async_client.get("/docs", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/doc"
