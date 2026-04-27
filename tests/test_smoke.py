"""Smoke tests: verify the package wires up correctly."""

from __future__ import annotations

import asyncio

import pytest

from utility_mcp_server import build_app, create_mcp
from utility_mcp_server.docs_client import (
    API_REGISTRY,
    DocsNotFound,
    PinelabsDocsClient,
)


def test_build_app_returns_asgi_app() -> None:
    app = build_app()
    assert callable(app)


def test_create_mcp_registers_tools() -> None:
    mcp = create_mcp()
    assert mcp.name == "utility-mcp-server"


def test_registry_contains_expected_apis() -> None:
    assert "init" in API_REGISTRY
    assert "doTransaction" in API_REGISTRY


@pytest.mark.asyncio
async def test_unknown_api_raises() -> None:
    client = PinelabsDocsClient(base_url="https://example.invalid")
    try:
        with pytest.raises(DocsNotFound):
            await client.get_documentation("nonexistent")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(test_unknown_api_raises())
