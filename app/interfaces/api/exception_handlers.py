"""Central API exception mapping."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.application.errors import (
    ApplicationError,
    AuthorizationError,
    NotFoundError,
    RateLimitExceededError,
    ValidationError,
)
from app.domain.errors import DomainError


def _error_body(
    code: str, message: str, details: dict[str, object] | None = None
) -> dict[str, object]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


def _status_for_application_error(exc: ApplicationError) -> int:
    if isinstance(exc, NotFoundError):
        return 404
    if isinstance(exc, AuthorizationError):
        return 401
    if isinstance(exc, RateLimitExceededError):
        return 429
    if isinstance(exc, ValidationError):
        return 400
    return 400


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        _ = request
        return JSONResponse(
            status_code=_status_for_application_error(exc),
            content=_error_body(code=exc.code, message=str(exc)),
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        _ = request
        return JSONResponse(
            status_code=400,
            content=_error_body(code=exc.code, message=str(exc)),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        _ = request
        return JSONResponse(
            status_code=422,
            content=_error_body(
                code="request_validation_error",
                message="Request validation failed",
                details={"errors": exc.errors()},
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        _ = request
        return JSONResponse(
            status_code=500,
            content=_error_body(code="internal_error", message="Internal server error"),
        )
