"""Integration tests for admin pack management and provisioning flows."""

import pytest
from app.core.security import hash_password
from app.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_admin_pack_and_user_provisioning(async_client, session_maker) -> None:
    """Admin user can manage packs, list stickers, and create owner accounts."""
    async with session_maker() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_email("admin@example.com")
        if existing is None:
            await repo.create_user_with_role(
                email="admin@example.com",
                password_hash=hash_password("password123"),
                is_admin=True,
            )

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    overview_response = await async_client.get("/api/v1/admin/overview", headers=admin_headers)
    assert overview_response.status_code == 200
    assert overview_response.json()["users"] >= 1

    generate_response = await async_client.post(
        "/api/v1/admin/packs/generate",
        headers=admin_headers,
        json={"quantity": 3},
    )
    assert generate_response.status_code == 201
    payload = generate_response.json()
    assert len(payload["stickers"]) == 3
    pack_id = payload["pack"]["id"]
    pack_code = payload["pack"]["pack_code"]

    list_response = await async_client.get("/api/v1/admin/packs", headers=admin_headers)
    assert list_response.status_code == 200
    assert any(pack["id"] == pack_id for pack in list_response.json()["packs"])

    pack_stickers_response = await async_client.get(
        f"/api/v1/admin/packs/{pack_id}/stickers",
        headers=admin_headers,
    )
    assert pack_stickers_response.status_code == 200
    assert len(pack_stickers_response.json()["stickers"]) == 3

    create_user_response = await async_client.post(
        "/api/v1/admin/users/create-and-assign-pack",
        headers=admin_headers,
        json={
            "email": "owner2@example.com",
            "password": "password123",
            "pack_code": pack_code,
        },
    )
    assert create_user_response.status_code == 201
    assert create_user_response.json()["assigned_pack_code"] == pack_code
