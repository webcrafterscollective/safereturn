"""Integration tests for login, refresh rotation, and logout token revocation."""

import pytest


@pytest.mark.asyncio
async def test_auth_login_refresh_logout(async_client, sample_user) -> None:
    """Create user fixture then validate full auth token lifecycle."""
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert "access_token" in login_payload
    assert "refresh_token" in login_payload

    first_refresh_token = login_payload["refresh_token"]

    refresh_response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()
    assert refresh_payload["refresh_token"] != first_refresh_token

    logout_response = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_payload["refresh_token"]},
    )
    assert logout_response.status_code == 204

    reuse_response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_payload["refresh_token"]},
    )
    assert reuse_response.status_code == 401
