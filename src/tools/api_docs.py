"""MCP tools for Pine Labs SDK API documentation (remote source)."""

from __future__ import annotations

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from ..logging_config import logger
from ..services.docs_client import docs_client


def _text_response(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def register(mcp: FastMCP) -> None:
    """Attach the documentation-related tools to the MCP server."""

    @mcp.tool(
        name="list_pinelabs_apis",
        description=(
            "List all available Pine Labs SDK API names "
            "(e.g. 'init', 'doTransaction', 'checkStatus'). Call this first "
            "to discover valid api_name values for 'get_api_documentation'."
        ),
    )
    async def list_pinelabs_apis() -> dict[str, Any]:
        logger.info("Tool invoked: list_pinelabs_apis")
        names = docs_client.known_apis()
        if not names:
            return _text_response("No APIs configured.")
        return _text_response("\n".join(names))

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
            "2. The documentation lists supported languages explicitly. "
            "If the user asks about a language NOT listed, reply that "
            "Pine Labs SDK does not document that language and stop — do "
            "NOT generate sample code in unsupported languages.\n"
            "3. If the user asks for a parameter, error, or behavior that "
            "is not in the returned doc, say 'not documented' instead of "
            "guessing.\n"
            "4. Quote field names, types and error variants verbatim.\n"
            "5. If unsure which api_name to use, call 'list_pinelabs_apis' "
            "first; never guess an api_name."
            "6. Do not return the code in any other language other than the one mentioned in the documentation. If the documentation does not mention any language, then do not return any code."
        ),
    )
    async def get_api_documentation(api_name: str) -> dict[str, Any]:
        logger.info("Tool invoked: get_api_documentation(api_name=%r)", api_name)
        if not api_name or not api_name.strip():
            return _text_response("Error: 'api_name' is required and cannot be empty.")

        api_name = api_name.strip()
        try:
            markdown, source_url = await docs_client.get_documentation(api_name)
        except KeyError:
            available = ", ".join(docs_client.known_apis()) or "none"
            logger.warning("API not found: %s", api_name)
            return _text_response(
                f"API '{api_name}' not found. Available APIs: {available}"
            )
        except httpx.HTTPError as exc:
            logger.exception("Failed to fetch documentation for %s", api_name)
            return _text_response(
                f"Error fetching documentation for '{api_name}': {exc}"
            )

        wrapped = (
            "=== AUTHORITATIVE PINE LABS SDK DOCUMENTATION ===\n"
            f"api_name: {api_name}\n"
            f"source_url: {source_url}\n"
            "\n"
            "RULES FOR THE ASSISTANT (do NOT ignore):\n"
            "- Answer ONLY using facts present below. If a detail is "
            "missing, say it is not documented.\n"
            "- Do NOT produce code in any language not listed in the "
            "Code Examples section below.\n"
            "- Do NOT invent parameter names, error variants, or return "
            "types that are not in the spec below.\n"
            "- Quote identifiers verbatim.\n"
            "\n"
            "--- BEGIN DOCUMENTATION ---\n"
            f"{markdown}"
            "--- END DOCUMENTATION ---\n"
        )
        return _text_response(wrapped)
