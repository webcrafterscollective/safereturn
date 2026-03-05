"""Centralized error classes and JSON error response handlers."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Application-level exception with explicit error code and status.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable explanation.
        status_code: HTTP status code.
        details: Optional extra details for debugging.
    """

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


def _error_envelope(
    code: str, message: str, details: dict[str, str] | None = None
) -> dict[str, object]:
    """Return consistent JSON error envelope used by all handlers."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


def register_error_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to FastAPI app instance."""

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        detail_text = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope("HTTP_ERROR", detail_text),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_envelope(
                "VALIDATION_ERROR", "Validation failed", {"errors": str(exc.errors())}
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=_error_envelope("INTERNAL_SERVER_ERROR", "Unexpected server error"),
        )
