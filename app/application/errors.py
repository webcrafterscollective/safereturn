"""Application-level exceptions mapped to API errors."""

from __future__ import annotations


class ApplicationError(Exception):
    """Base class for use-case execution errors."""

    code = "application_error"


class NotFoundError(ApplicationError):
    code = "not_found"


class AuthorizationError(ApplicationError):
    code = "forbidden"


class ValidationError(ApplicationError):
    code = "validation_error"


class RateLimitExceededError(ApplicationError):
    code = "rate_limited"
