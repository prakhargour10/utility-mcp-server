"""MCP tool registration entry points."""

from mcp.server.fastmcp import FastMCP

from .api_docs import register as register_api_docs
from .sdk_download import register as register_sdk_download


def register_all(mcp: FastMCP) -> None:
    """Register every tool on the given FastMCP instance."""
    register_api_docs(mcp)
    register_sdk_download(mcp)
