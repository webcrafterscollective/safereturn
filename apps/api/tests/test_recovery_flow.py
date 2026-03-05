"""Integration test for end-to-end recovery flow: register, scan, and relay messages."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_recovery_scan_and_anonymous_relay(async_client, sample_user) -> None:
    """Validate owner and finder can communicate through session relay."""
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": sample_user["email"], "password": sample_user["password"]},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    owner_headers = {"Authorization": f"Bearer {access_token}"}
    sticker_code = f"SAFE-{uuid4().hex[:10].upper()}"

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

    owner_reply_response = await async_client.post(
        f"/api/v1/recovery/owner/sessions/{session_reference}/messages",
        headers=owner_headers,
        json={"message_body": "Thank you. I can meet at 7 PM near the station."},
    )
    assert owner_reply_response.status_code == 201
    assert owner_reply_response.json()["sender_role"] == "owner"
