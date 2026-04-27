"""FastMCP server factory for the utility MCP server."""

from __future__ import annotations

import contextlib
import logging
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .config import Settings, get_settings
from .logging_config import configure_logging
from .services.pinelabs_docs import PinelabsDocsClient
from .tools import api_docs as api_docs_tools
from .tools import sdk as sdk_tools

logger = logging.getLogger(__name__)


def create_mcp(settings: Settings | None = None) -> FastMCP:
    """Build a FastMCP instance with all tools registered."""
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    docs_client = PinelabsDocsClient(
        base_url=settings.docs_base_url,
        timeout=settings.docs_http_timeout,
        retries=settings.docs_http_retries,
        cache_ttl_seconds=settings.docs_cache_ttl_seconds,
    )

    @contextlib.asynccontextmanager
    async def lifespan(_mcp: FastMCP) -> AsyncIterator[None]:
        logger.info("utility-mcp-server starting")
        try:
            yield
        finally:
            logger.info("utility-mcp-server shutting down; closing http client")
            await docs_client.aclose()

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
        lifespan=lifespan,
    )

    api_docs_tools.register(mcp, docs_client)
    sdk_tools.register(mcp, settings.sdk_dir, settings.sdk_download_base_url)

    return mcp


def build_app(settings: Settings | None = None):
    """Build the ASGI app exposed at /mcp."""
    mcp = create_mcp(settings)
    return mcp.streamable_http_app()
