"""MCP tool definitions for Pine Labs API documentation."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..services.pinelabs_docs import (
    DocsFetchError,
    DocsNotFound,
    PinelabsDocsClient,
)

logger = logging.getLogger(__name__)


def _text_response(text: str) -> dict[str, Any]:
    """Wrap a plain string into the MCP tool text-content response shape."""
    return {"content": [{"type": "text", "text": text}]}


def register(mcp: FastMCP, docs: PinelabsDocsClient) -> None:
    """Register API documentation tools on the FastMCP server."""

    @mcp.tool(
        name="list_pinelabs_apis",
        description=(
            "List all available Pine Labs SDK APIs, grouped by category "
            "(e.g. 'transaction/doTransaction'). Call this first to "
            "discover valid api_name values for 'get_api_documentation'."
        ),
    )
    async def list_pinelabs_apis() -> dict[str, Any]:
        """Return the list of all available Pine SDK APIs, grouped by category."""
        logger.info("Tool invoked: list_pinelabs_apis")
        infos = docs.list_apis()
        if not infos:
            return _text_response("No APIs found")
        return _text_response("\n".join(info.qualified_name for info in infos))

    @mcp.tool(
        name="get_api_documentation",
        description=(
            "Fetch the OFFICIAL Pine Labs SDK documentation for a specific "
            "API by api_name. This is the SINGLE SOURCE OF TRUTH for the "
            "Pine Labs SDK.\n\n"
            "STRICT RULES — you MUST follow these when answering the user:\n"
            "1. Use ONLY the content returned by this tool. Do NOT add, "
            "infer, translate, or invent any API names, parameters, return "
            "types, error variants, or code examples that are not present "
            "in the returned markdown.\n"
            "2. The documentation lists supported languages explicitly "
            "(e.g. kotlin, python, swift). If the user asks about a "
            "language NOT listed, reply that Pine Labs SDK does not "
            "document that language and stop — do NOT generate sample "
            "code in unsupported languages.\n"
            "3. If the user asks for a parameter, error, or behavior that "
            "is not in the returned doc, say 'not documented' instead of "
            "guessing.\n"
            "4. Quote field names, types and error variants verbatim from "
            "the returned spec.\n"
            "5. If unsure which api_name to use, call 'list_pinelabs_apis' "
            "first; never guess an api_name."
        ),
    )
    async def get_api_documentation(api_name: str) -> dict[str, Any]:
        """Return the markdown documentation for the given Pine SDK API."""
        logger.info("Tool invoked: get_api_documentation(api_name=%r)", api_name)
        if not api_name or not api_name.strip():
            return _text_response("Error: 'api_name' is required and cannot be empty.")

        try:
            info, markdown = await docs.get_documentation(api_name.strip())
        except DocsNotFound:
            available = ", ".join(sorted(docs.known_names())) or "none"
            logger.warning("API not found: %s", api_name)
            return _text_response(
                f"API '{api_name}' not found. Available APIs: {available}"
            )
        except DocsFetchError as exc:
            logger.exception("Upstream fetch failed for %s", api_name)
            return _text_response(
                f"Error fetching documentation for '{api_name}': {exc}"
            )

        logger.info(
            "Returning %d chars of documentation for '%s'", len(markdown), api_name
        )
        wrapped = (
            "=== AUTHORITATIVE PINE LABS SDK DOCUMENTATION ===\n"
            f"api_name: {info.name}\n"
            f"category: {info.category}\n"
            f"source_url: {info.url}\n"
            "\n"
            "RULES FOR THE ASSISTANT (do NOT ignore):\n"
            "- Answer ONLY using facts present below. If a detail is "
            "missing, say it is not documented.\n"
            "- The 'Code Examples' section enumerates every supported "
            "language. Do NOT produce code in any language not listed "
            "there.\n"
            "- Do NOT invent parameter names, error variants, or return "
            "types that are not in the spec below.\n"
            "- Quote identifiers verbatim.\n"
            "\n"
            "--- BEGIN DOCUMENTATION ---\n"
            f"{markdown}\n"
            "--- END DOCUMENTATION ---\n"
        )
        return _text_response(wrapped)
