"""Smoke tests: verify the package wires up correctly."""

from __future__ import annotations

from utility_mcp_server import build_app, create_mcp
from utility_mcp_server.tools import _is_list_documents_query


def test_build_app_returns_asgi_app() -> None:
    app = build_app()
    assert callable(app)


def test_create_mcp_registers_tools() -> None:
    mcp = create_mcp()
    assert mcp.name == "utility-mcp-server"


def test_list_documents_intent_detection() -> None:
    assert _is_list_documents_query("list all the documents available")
    assert _is_list_documents_query("what docs are available?")
    assert _is_list_documents_query("show me all available APIs")
    assert not _is_list_documents_query("how do I initialize the SDK?")
    assert not _is_list_documents_query("list the parameters of init")
