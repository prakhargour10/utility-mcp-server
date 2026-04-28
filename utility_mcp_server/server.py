"""FastMCP server factory and ASGI app."""

from __future__ import annotations

import asyncio
import atexit
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from . import tools
from .config import Settings, get_settings
from .docs_client import DocsFetchError, PinelabsDocsClient

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


def _build_components(settings: Settings) -> tuple[FastMCP, PinelabsDocsClient]:
    docs_client = PinelabsDocsClient(
        base_url=settings.docs_base_url,
        timeout=settings.docs_http_timeout,
        retries=settings.docs_http_retries,
        cache_ttl_seconds=settings.docs_cache_ttl_seconds,
    )
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
    return mcp, docs_client


def create_mcp(settings: Settings | None = None) -> FastMCP:
    """Build a FastMCP instance with all tools registered."""
    settings = settings or get_settings()
    _configure_logging(settings.log_level)
    mcp, _ = _build_components(settings)
    return mcp


async def _prewarm_docs_cache(docs_client: PinelabsDocsClient) -> None:
    """Fetch every known API in parallel so the first client request is fast."""
    names = list(docs_client.known_names())
    if not names:
        return
    logger.info("Pre-warming docs cache for %d APIs: %s", len(names), names)

    async def _fetch_one(name: str) -> None:
        try:
            await docs_client.get_documentation(name)
            logger.info("Pre-warmed cache for %r", name)
        except DocsFetchError as exc:
            logger.warning("Pre-warm failed for %r: %s", name, exc)

    await asyncio.gather(*(_fetch_one(n) for n in names), return_exceptions=False)


def _wrap_session_not_found(asgi_app):
    """Rewrite the upstream "Session not found" JSON-RPC error to include guidance.

    The MCP streamable-HTTP transport returns a 404 with body
    ``{"error": {"message": "Session not found", ...}}`` when a client sends a
    request with an unknown/expired session id. We rewrite that message in-place
    so clients see actionable guidance.
    """
    target = b'"message":"Session not found"'
    replacement = b'"message":"Session not found, Please restart the server"'

    async def app(scope, receive, send):
        if scope.get("type") != "http":
            await asgi_app(scope, receive, send)
            return

        state = {"rewrite": False, "headers": None, "start": None}

        async def _send(message):
            mtype = message.get("type")
            if mtype == "http.response.start":
                if message.get("status") == 404:
                    state["rewrite"] = True
                    state["start"] = message
                    return  # defer until we see the body
                await send(message)
            elif mtype == "http.response.body" and state["rewrite"]:
                body = message.get("body", b"") or b""
                more = message.get("more_body", False)
                if more:
                    # Streaming 404 — bail out of rewriting; flush as-is.
                    if state["start"] is not None:
                        await send(state["start"])
                        state["start"] = None
                    state["rewrite"] = False
                    await send(message)
                    return
                if target in body:
                    body = body.replace(target, replacement)
                    start = state["start"] or {}
                    headers = [
                        (k, v)
                        for (k, v) in start.get("headers", [])
                        if k.lower() != b"content-length"
                    ]
                    headers.append((b"content-length", str(len(body)).encode("ascii")))
                    start = {**start, "headers": headers}
                    await send(start)
                    await send({"type": "http.response.body", "body": body, "more_body": False})
                else:
                    if state["start"] is not None:
                        await send(state["start"])
                        state["start"] = None
                    await send(message)
                state["rewrite"] = False
            else:
                await send(message)

        await asgi_app(scope, receive, _send)

    return app


def build_app(settings: Settings | None = None):
    """Build the ASGI app exposed at /mcp, with docs cache pre-warming on startup."""
    settings = settings or get_settings()
    _configure_logging(settings.log_level)
    mcp, docs_client = _build_components(settings)
    asgi_app = mcp.streamable_http_app()

    # Wrap the existing Starlette lifespan to also kick off cache pre-warming.
    import contextlib

    original_lifespan = asgi_app.router.lifespan_context

    @contextlib.asynccontextmanager
    async def _wrapped_lifespan(app):
        async with original_lifespan(app):
            # Fire-and-forget so startup isn't blocked by upstream latency.
            asyncio.create_task(_prewarm_docs_cache(docs_client))
            yield

    asgi_app.router.lifespan_context = _wrapped_lifespan
    return _wrap_session_not_found(asgi_app)


# Module-level ASGI app — used by uvicorn target ``utility_mcp_server.server:app``.
app = build_app()

