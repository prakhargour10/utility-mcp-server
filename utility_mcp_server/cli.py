"""CLI entrypoint for the utility MCP server."""

from __future__ import annotations

import uvicorn

from .config import get_settings


def main() -> None:
    """Run the ASGI app via uvicorn using settings from the environment."""
    settings = get_settings()
    uvicorn.run(
        "utility_mcp_server.server:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
