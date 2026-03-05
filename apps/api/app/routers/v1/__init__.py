"""Version 1 router package."""

from app.routers.v1 import admin, auth, health, metrics, recovery

__all__ = ["admin", "auth", "health", "metrics", "recovery"]
