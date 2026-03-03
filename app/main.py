"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from app.interfaces.api.exception_handlers import install_exception_handlers
from app.interfaces.api.v1.dependencies import build_container
from app.interfaces.api.v1.routers.admin import router as admin_router
from app.interfaces.api.v1.routers.auth import router as auth_router
from app.interfaces.api.v1.routers.delivery import router as delivery_router
from app.interfaces.api.v1.routers.owner import router as owner_router
from app.interfaces.api.v1.routers.public import router as public_router
from app.settings import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.state.container = build_container()

app.include_router(auth_router)
app.include_router(owner_router)
app.include_router(public_router)
app.include_router(admin_router)
app.include_router(delivery_router)

install_exception_handlers(app)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
