from __future__ import annotations

import pytest

from app.interfaces.api.v1.dependencies import build_container
from app.main import app


@pytest.fixture(autouse=True)
def reset_container_state() -> None:
    """Ensure each test runs with isolated in-memory application state."""
    app.state.container = build_container()
