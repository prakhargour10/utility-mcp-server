"""FastMCP server factory and ASGI app."""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from . import tools
from .config import Settings, get_settings

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


def _build_mcp(settings: Settings) -> FastMCP:
    mcp = FastMCP(
        name="utility-mcp-server",
        instructions=(
            "A utility MCP server providing Pine Labs SDK download links "
            "and RAG-grounded answers over the official documentation."
        ),
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=settings.allowed_hosts,
        ),
    )
    tools.register(mcp, settings)
    return mcp


def create_mcp(settings: Settings | None = None) -> FastMCP:
    """Build a FastMCP instance with all tools registered."""
    settings = settings or get_settings()
    _configure_logging(settings.log_level)
    return _build_mcp(settings)


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
                    await send(
                        {"type": "http.response.body", "body": body, "more_body": False}
                    )
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
    """Build the ASGI app exposed at /mcp."""
    settings = settings or get_settings()
    _configure_logging(settings.log_level)
    mcp = _build_mcp(settings)
    return _wrap_session_not_found(mcp.streamable_http_app())


# Module-level ASGI app — used by uvicorn target ``utility_mcp_server.server:app``.
app = build_app()
