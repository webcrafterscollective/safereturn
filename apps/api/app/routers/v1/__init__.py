"""Version 1 router package."""

from app.routers.v1 import auth, health, metrics, recovery

__all__ = ["auth", "health", "metrics", "recovery"]
