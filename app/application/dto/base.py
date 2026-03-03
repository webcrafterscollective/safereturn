"""Base DTO marker for application boundaries."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DTO:
    """Marker type for application input/output contracts."""
