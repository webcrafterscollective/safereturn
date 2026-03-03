"""Domain-level exceptions with stable error codes."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain rule violations."""

    code = "domain_error"


class InvariantViolationError(DomainError):
    """Raised when an entity invariant would be violated."""

    code = "invariant_violation"
