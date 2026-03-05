"""Integration test for recovery flow with admin-generated sticker packs."""

import pytest
from app.core.security import hash_password
from app.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_recovery_scan_and_anonymous_relay(async_client, session_maker) -> None:
    """Validate claim -> register -> scan -> relay workflow."""
    async with session_maker() as session:
        repo = UserRepository(session)
        existing_admin = await repo.get_by_email("owner.admin@example.com")
        if existing_admin is None:
            await repo.create_user_with_role(
                email="owner.admin@example.com",
                password_hash=hash_password("password123"),
                is_admin=True,
            )

    register_response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "owner.secondary@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "owner.admin@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {access_token}"}

    pack_response = await async_client.post(
        "/api/v1/admin/packs/generate",
        headers=owner_headers,
        json={"quantity": 1},
    )
    assert pack_response.status_code == 201
    sticker_code = pack_response.json()["stickers"][0]["code"]
    pack_code = pack_response.json()["pack"]["pack_code"]

    claim_response = await async_client.post(
        "/api/v1/recovery/packs/claim",
        headers=owner_headers,
        json={"pack_code": pack_code},
    )
    assert claim_response.status_code == 200
    assert claim_response.json()["total_stickers"] == 1

    register_response = await async_client.post(
        "/api/v1/recovery/stickers/register",
        headers=owner_headers,
        json={
            "sticker_code": sticker_code,
            "item_name": "Office Laptop Bag",
            "item_category": "bag",
            "item_description": "Black backpack with laptop",
        },
    )
    assert register_response.status_code == 201
    register_payload = register_response.json()
    item_id = register_payload["item_id"]

    lost_response = await async_client.post(
        f"/api/v1/recovery/items/{item_id}/mark-lost",
        headers=owner_headers,
        json={"last_known_location": "Metro Station", "notes": "Left near gate 2"},
    )
    assert lost_response.status_code == 201

    scan_response = await async_client.post(
        "/api/v1/recovery/scan",
        json={"sticker_code": sticker_code, "finder_note": "Found near platform"},
    )
    assert scan_response.status_code == 200
    session_token = scan_response.json()["session_token"]

    finder_message_response = await async_client.post(
        f"/api/v1/recovery/sessions/{session_token}/messages",
        json={"message_body": "I found your bag and can hand it over this evening."},
    )
    assert finder_message_response.status_code == 201
    finder_message_payload = finder_message_response.json()
    assert finder_message_payload["sender_role"] == "finder"
    session_reference = finder_message_payload["session_reference"]

    owner_inbox_response = await async_client.get(
        "/api/v1/recovery/owner/messages",
        headers=owner_headers,
    )
    assert owner_inbox_response.status_code == 200
    assert len(owner_inbox_response.json()["messages"]) >= 1

    items_response = await async_client.get("/api/v1/recovery/items/mine", headers=owner_headers)
    assert items_response.status_code == 200
    assert any(item["item_id"] == item_id for item in items_response.json()["items"])

    owner_reply_response = await async_client.post(
        f"/api/v1/recovery/owner/sessions/{session_reference}/messages",
        headers=owner_headers,
        json={"message_body": "Thank you. I can meet at 7 PM near the station."},
    )
    assert owner_reply_response.status_code == 201
    assert owner_reply_response.json()["sender_role"] == "owner"

    claim_issue_response = await async_client.post(
        "/api/v1/recovery/claim-issues",
        json={
            "sticker_code": sticker_code,
            "note": "Testing issue reporting flow from recovery test.",
        },
    )
    assert claim_issue_response.status_code == 201

    mark_found_response = await async_client.post(
        f"/api/v1/recovery/items/{item_id}/mark-found",
        headers=owner_headers,
    )
    assert mark_found_response.status_code == 204
