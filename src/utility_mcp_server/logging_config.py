"""Centralized logging configuration."""

from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once. Idempotent."""
    root = logging.getLogger()
    if getattr(root, "_utility_mcp_configured", False):
        return
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    root._utility_mcp_configured = True  # type: ignore[attr-defined]
