"""Custom middleware utilities for request IDs and security headers."""

from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response

from app.core.logging import request_id_ctx_var

DEFAULT_CSP = (
    "default-src 'self'; "
    "img-src 'self' data:; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; "
    "connect-src 'self'"
)

DOCS_CSP = (
    "default-src 'self'; "
    "img-src 'self' data:; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline'; "
    "connect-src 'self'"
)


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Attach a stable request ID to context and response headers."""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    token = request_id_ctx_var.set(request_id)
    try:
        response = await call_next(request)
    finally:
        request_id_ctx_var.reset(token)

    response.headers["X-Request-ID"] = request_id
    return response


async def security_headers_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Add security headers.

    Swagger UI bootstraps with inline script, so we use a docs-only CSP policy
    while keeping the stricter default policy for all other routes.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    docs_prefixes = ("/doc", "/docs", "/swagger-assets")
    if request.url.path.startswith(docs_prefixes):
        response.headers["Content-Security-Policy"] = DOCS_CSP
    else:
        response.headers["Content-Security-Policy"] = DEFAULT_CSP

    return response
