from __future__ import annotations

from app.infrastructure.security.rate_limiter import InMemoryRateLimiter


def test_rate_limiter_blocks_after_threshold() -> None:
    limiter = InMemoryRateLimiter()

    for _ in range(3):
        assert limiter.allow(key="k1", limit=3, window_seconds=60) is True

    assert limiter.allow(key="k1", limit=3, window_seconds=60) is False
