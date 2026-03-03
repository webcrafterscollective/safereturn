"""Process-local token bucket limiter."""

from __future__ import annotations

import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        oldest_allowed = now - window_seconds
        events = self._events[key]
        while events and events[0] < oldest_allowed:
            events.popleft()
        if len(events) >= limit:
            return False
        events.append(now)
        return True
