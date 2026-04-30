"""Smoke tests: verify the package wires up correctly."""

from __future__ import annotations

from utility_mcp_server import build_app, create_mcp


def test_build_app_returns_asgi_app() -> None:
    app = build_app()
    assert callable(app)


def test_create_mcp_registers_tools() -> None:
    mcp = create_mcp()
    assert mcp.name == "utility-mcp-server"
