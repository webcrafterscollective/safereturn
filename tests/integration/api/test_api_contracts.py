from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_end_to_end_flow_and_pii_protection() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        register_response = await client.post(
            "/auth/register",
            json={"email": "owner@example.com", "phone": None},
        )
        assert register_response.status_code == 201

        login_response = await client.post(
            "/auth/login",
            json={"email_or_phone": "owner@example.com", "otp_or_password_stub": "123456"},
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]

        admin_response = await client.post(
            "/admin/tags/batch-create",
            headers={"x-admin-api-key": "dev-admin-key"},
            json={"count": 1},
        )
        assert admin_response.status_code == 201
        created_tag = admin_response.json()["tags"][0]

        claim_response = await client.post(
            "/tags/claim",
            headers={"authorization": f"Bearer {access_token}"},
            json={"claim_code": created_tag["claim_code"]},
        )
        assert claim_response.status_code == 200
        tag_id = claim_response.json()["tag_id"]
        public_token = claim_response.json()["public_token"]

        item_response = await client.post(
            "/items",
            headers={"authorization": f"Bearer {access_token}"},
            json={
                "tag_id": tag_id,
                "name": "Laptop",
                "category": "electronics",
                "notes": "Blue sleeve",
            },
        )
        assert item_response.status_code == 201
        item_id = item_response.json()["item_id"]

        lost_response = await client.post(
            f"/items/{item_id}/lost",
            headers={"authorization": f"Bearer {access_token}"},
        )
        assert lost_response.status_code == 200
        assert lost_response.json()["is_lost"] is True

        public_response = await client.get(f"/p/{public_token}")
        assert public_response.status_code == 200
        public_payload = public_response.json()
        assert "owner@example.com" not in str(public_payload)
        assert "safe_item_label" in public_payload

        session_response = await client.post(f"/p/{public_token}/sessions")
        assert session_response.status_code == 201
        finder_session_token = session_response.json()["finder_session_token"]

        finder_message = await client.post(
            f"/p/{public_token}/message",
            json={
                "finder_session_token": finder_session_token,
                "message_body": "I found it near the library entrance.",
            },
        )
        assert finder_message.status_code == 201
        conversation_id = finder_message.json()["conversation_id"]

        conversations_response = await client.get(
            "/conversations",
            headers={"authorization": f"Bearer {access_token}"},
        )
        assert conversations_response.status_code == 200
        assert conversations_response.json()["conversations"]

        owner_reply = await client.post(
            f"/conversations/{conversation_id}/messages",
            headers={"authorization": f"Bearer {access_token}"},
            json={"message_body": "Thanks. I can come in 10 minutes."},
        )
        assert owner_reply.status_code == 201

        finder_poll = await client.get(
            f"/p/{public_token}/messages",
            params={"finder_session_token": finder_session_token},
        )
        assert finder_poll.status_code == 200
        bodies = [item["body"] for item in finder_poll.json()["messages"]]
        assert "Thanks. I can come in 10 minutes." in bodies

        delivery_create = await client.post(
            "/deliveries",
            headers={"authorization": f"Bearer {access_token}"},
            json={
                "conversation_id": conversation_id,
                "pickup_drop_details_stub": {"pickup": "Gate 1", "drop": "Hostel"},
            },
        )
        assert delivery_create.status_code == 201
        delivery_id = delivery_create.json()["delivery_id"]

        delivery_get = await client.get(
            f"/deliveries/{delivery_id}",
            headers={"authorization": f"Bearer {access_token}"},
        )
        assert delivery_get.status_code == 200
        assert delivery_get.json()["status"] == "booked"

        refresh_response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_response.status_code == 200

        logout_response = await client.post(
            "/auth/logout",
            headers={"authorization": f"Bearer {access_token}"},
        )
        assert logout_response.status_code == 200
        assert logout_response.json()["success"] is True


@pytest.mark.asyncio
async def test_rate_limited_message_returns_consistent_error_shape() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        admin_response = await client.post(
            "/admin/tags/batch-create",
            headers={"x-admin-api-key": "dev-admin-key"},
            json={"count": 1},
        )
        public_token = admin_response.json()["tags"][0]["public_token"]

        session_response = await client.post(f"/p/{public_token}/sessions")
        finder_session_token = session_response.json()["finder_session_token"]

        for _ in range(20):
            await client.post(
                f"/p/{public_token}/message",
                json={
                    "finder_session_token": finder_session_token,
                    "message_body": "Ping",
                },
            )

        blocked = await client.post(
            f"/p/{public_token}/message",
            json={
                "finder_session_token": finder_session_token,
                "message_body": "Ping",
            },
        )
        assert blocked.status_code == 429
        error = blocked.json()["error"]
        assert error["code"] == "rate_limited"
        assert "details" in error
