"""FastAPI application entrypoint and composition root.

This module wires middleware, routers, structured logging, and SPA static serving.
Swagger UI is intentionally exposed at `/doc` per project contract.
"""

import logging
import time
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path

from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import request_id_middleware, security_headers_middleware
from app.core.settings import get_settings
from app.metrics.prometheus import REQUEST_COUNT, REQUEST_LATENCY
from app.routers.v1 import auth, health, metrics

logger = logging.getLogger(__name__)
SWAGGER_OAUTH2_REDIRECT_PATH = "/doc/oauth2-redirect"


class ImmutableStaticFiles(StaticFiles):
    """StaticFiles variant that applies immutable cache headers for built assets."""

    async def get_response(self, path: str, scope: MutableMapping[str, Any]) -> Any:
        """Serve static file and add long-lived cache header."""
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


def create_app() -> FastAPI:
    """Create and configure FastAPI app instance."""
    settings = get_settings()
    configure_logging(settings.log_level)

    application = FastAPI(
        title=settings.app_name,
        docs_url=None,
        openapi_url="/openapi.json",
        redoc_url=None,
        swagger_ui_oauth2_redirect_url=SWAGGER_OAUTH2_REDIRECT_PATH,
    )
    application.openapi_version = "3.0.3"

    # Security defaults.
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts_list)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # Request context and security middleware.
    application.middleware("http")(request_id_middleware)
    application.middleware("http")(security_headers_middleware)

    @application.middleware("http")
    async def metrics_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Collect request count and latency metrics for Prometheus."""
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        path = request.url.path
        method = request.method
        status = str(response.status_code)

        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(elapsed)
        return response

    # Routers: API versioned routes plus infra endpoints.
    application.include_router(auth.router, prefix="/api/v1")
    application.include_router(health.router)
    application.include_router(metrics.router)

    register_error_handlers(application)

    # Serve vendored Swagger UI assets from local origin to satisfy strict CSP.
    application.mount(
        "/swagger-assets",
        StaticFiles(directory=str(swagger_ui_path), html=False),
        name="swagger-assets",
    )

    @application.api_route("/doc", methods=["GET", "HEAD"], include_in_schema=False)
    async def swagger_ui() -> Response:
        """Serve Swagger UI using same-origin JS/CSS/favicon assets."""
        return get_swagger_ui_html(
            openapi_url=application.openapi_url or "/openapi.json",
            title=f"{settings.app_name} - Swagger UI",
            oauth2_redirect_url=application.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/swagger-assets/swagger-ui-bundle.js",
            swagger_css_url="/swagger-assets/swagger-ui.css",
            swagger_favicon_url="/swagger-assets/favicon-32x32.png",
        )

    @application.get(
        SWAGGER_OAUTH2_REDIRECT_PATH,
        include_in_schema=False,
    )
    async def swagger_ui_redirect() -> Response:
        """Serve OAuth2 redirect helper page for Swagger UI."""
        return get_swagger_ui_oauth2_redirect_html()

    @application.api_route("/docs", methods=["GET", "HEAD"], include_in_schema=False)
    async def docs_backward_compat() -> Response:
        """Keep backward compatibility for clients expecting /docs."""
        return RedirectResponse(url="/doc", status_code=307)

    frontend_dist = settings.computed_frontend_dist_path
    assets_dir = frontend_dist / "assets"

    # Serve compiled SPA assets from /assets with immutable caching.
    if assets_dir.exists():
        application.mount(
            "/assets",
            ImmutableStaticFiles(directory=str(assets_dir), html=False),
            name="assets",
        )
    else:
        logger.warning("Frontend assets directory not found", extra={"path": str(assets_dir)})

    @application.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str) -> Response:
        """Serve SPA index for unknown client-side routes.

        Protected prefixes are excluded to avoid collisions with API/docs/infra routes.
        """
        protected_prefixes = (
            "api/",
            "doc",
            "docs",
            "openapi.json",
            "redoc",
            "swagger-assets/",
            "assets/",
            "health/",
            "metrics",
        )
        if full_path.startswith(protected_prefixes):
            return JSONResponse(
                status_code=404,
                content={"error": {"code": "NOT_FOUND", "message": "Not found", "details": {}}},
            )

        index_file = frontend_dist / "index.html"
        if index_file.exists():
            response = FileResponse(index_file)
            response.headers["Cache-Control"] = "no-cache"
            return response

        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "FRONTEND_UNAVAILABLE",
                    "message": "Frontend build not found. Build apps/web to generate dist/.",
                    "details": {},
                }
            },
        )

    return application


app = create_app()
