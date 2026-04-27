"""Logging configuration."""

from __future__ import annotations

import logging

from .config import settings


def configure_logging() -> logging.Logger:
    """Configure root logging once and return the package logger."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("utility-mcp-server")


logger = configure_logging()
