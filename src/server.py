"""FastMCP server construction and ASGI app exposure."""

from __future__ import annotations

import contextlib
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .config import settings
from .logging_config import logger
from .services.docs_client import docs_client
from .tools import register_all


def build_mcp() -> FastMCP:
    """Construct the FastMCP instance with all tools registered."""
    instance = FastMCP(
        name=settings.server_name,
        instructions=settings.server_instructions,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=list(settings.allowed_hosts),
        ),
    )
    register_all(instance)
    logger.info("FastMCP server '%s' constructed", settings.server_name)
    return instance


mcp: FastMCP = build_mcp()


@contextlib.asynccontextmanager
async def _lifespan(_app) -> AsyncIterator[None]:
    """Cleanly close shared HTTP client on shutdown."""
    try:
        yield
    finally:
        await docs_client.aclose()
        logger.info("docs HTTP client closed")


# ASGI app — used by uvicorn directly (endpoint: /mcp)
app = mcp.streamable_http_app()
# Attach lifespan if the app supports it (Starlette).
with contextlib.suppress(AttributeError):
    app.router.lifespan_context = _lifespan  # type: ignore[attr-defined]
