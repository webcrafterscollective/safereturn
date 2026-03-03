"""Mock delivery provider adapter with simple state transitions."""

from __future__ import annotations


class MockDeliveryProvider:
    def __init__(self) -> None:
        self._status_by_ref: dict[str, str] = {}

    async def quote(self, payload: dict[str, str]) -> dict[str, str]:
        _ = payload
        return {"amount": "100", "currency": "INR"}

    async def book(self, payload: dict[str, str]) -> dict[str, str]:
        ref = f"mock-{len(self._status_by_ref) + 1}"
        _ = payload
        self._status_by_ref[ref] = "booked"
        return {"provider_ref": ref, "status": "booked"}

    async def cancel(self, provider_ref: str) -> dict[str, str]:
        self._status_by_ref[provider_ref] = "canceled"
        return {"status": "canceled"}

    async def track(self, provider_ref: str) -> dict[str, str]:
        return {"status": self._status_by_ref.get(provider_ref, "created")}
