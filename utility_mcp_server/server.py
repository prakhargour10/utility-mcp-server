"""FastMCP server factory and ASGI app."""

from __future__ import annotations

import atexit
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from . import tools
from .config import Settings, get_settings
from .docs_client import PinelabsDocsClient

logger = logging.getLogger(__name__)


def _configure_logging(level: str) -> None:
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


def create_mcp(settings: Settings | None = None) -> FastMCP:
    """Build a FastMCP instance with all tools registered."""
    settings = settings or get_settings()
    _configure_logging(settings.log_level)

    docs_client = PinelabsDocsClient(
        base_url=settings.docs_base_url,
        timeout=settings.docs_http_timeout,
        retries=settings.docs_http_retries,
        cache_ttl_seconds=settings.docs_cache_ttl_seconds,
    )

    # Close the shared HTTP client once on process exit.
    # NOTE: We deliberately do not use FastMCP's per-session lifespan here
    # because it runs once per MCP session, which would close the shared
    # client after the first session ends.
    atexit.register(docs_client.close_sync)

    mcp = FastMCP(
        name="utility-mcp-server",
        instructions=(
            "A utility MCP server providing Pine Labs SDK API documentation "
            "fetched live from the official docs site, plus SDK download links."
        ),
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=settings.allowed_hosts,
        ),
    )

    tools.register(
        mcp,
        docs_client,
        settings.sdk_dir,
        settings.sdk_download_base_url,
    )
    return mcp


def build_app(settings: Settings | None = None):
    """Build the ASGI app exposed at /mcp."""
    return create_mcp(settings).streamable_http_app()


# Module-level ASGI app — used by uvicorn target ``utility_mcp_server.server:app``.
app = build_app()
