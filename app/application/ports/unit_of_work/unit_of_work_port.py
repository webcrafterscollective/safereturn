from __future__ import annotations

from typing import Protocol


class UnitOfWorkPort(Protocol):
    async def __aenter__(self) -> UnitOfWorkPort: ...

    async def __aexit__(self, exc_type, exc, tb) -> None: ...  # type: ignore[no-untyped-def]

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
