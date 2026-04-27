"""All MCP tools for the utility server.

Currently exposes:

* ``list_pinelabs_apis`` — list available API names.
* ``get_api_documentation`` — fetch live markdown for an API.
* ``get_pinelabs_sdk_download_link`` — return public SDK download URL(s).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .docs_client import DocsFetchError, DocsNotFound, PinelabsDocsClient

logger = logging.getLogger(__name__)

_SDK_EXTENSIONS = {".aar", ".jar", ".zip", ".tar.gz", ".tgz", ".whl"}


def _text_response(text: str) -> dict[str, Any]:
    """Wrap a plain string into the MCP tool text-content response shape."""
    return {"content": [{"type": "text", "text": text}]}


def _discover_sdks(sdk_dir: Path) -> list[Path]:
    if not sdk_dir.exists():
        return []
    return sorted(
        p
        for p in sdk_dir.iterdir()
        if p.is_file()
        and (p.suffix.lower() in _SDK_EXTENSIONS or p.name.lower().endswith(".tar.gz"))
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def register(
    mcp: FastMCP,
    docs: PinelabsDocsClient,
    sdk_dir: Path,
    sdk_download_base_url: str,
) -> None:
    """Attach all tools to the FastMCP server."""
    _register_api_docs(mcp, docs)
    _register_sdk_download(mcp, sdk_dir, sdk_download_base_url)


# ---------------------------------------------------------------------------
# API documentation tools
# ---------------------------------------------------------------------------
def _register_api_docs(mcp: FastMCP, docs: PinelabsDocsClient) -> None:
    @mcp.tool(
        name="list_pinelabs_apis",
        description=(
            "List all available Pine Labs SDK APIs, grouped by category "
            "(e.g. 'transaction/doTransaction'). Call this first to "
            "discover valid api_name values for 'get_api_documentation'."
        ),
    )
    async def list_pinelabs_apis() -> dict[str, Any]:
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


# ---------------------------------------------------------------------------
# SDK download tool
# ---------------------------------------------------------------------------
def _register_sdk_download(
    mcp: FastMCP, sdk_dir: Path, download_base_url: str
) -> None:
    base = download_base_url.rstrip("/")

    @mcp.tool(
        name="get_pinelabs_sdk_download_link",
        description=(
            "Return the official download link(s) for the Pine Labs SDK "
            "artifact(s) (e.g. the Android .aar). Use this whenever a "
            "client asks where/how to download the Pine Labs SDK, the "
            "AAR file, or the SDK binary. Optionally pass 'sdk_name' to "
            "match a specific artifact filename (substring match, case-"
            "insensitive); omit to list all available SDK downloads."
        ),
    )
    async def get_pinelabs_sdk_download_link(sdk_name: str = "") -> dict[str, Any]:
        logger.info(
            "Tool invoked: get_pinelabs_sdk_download_link(sdk_name=%r)", sdk_name
        )
        sdks = _discover_sdks(sdk_dir)
        if not sdks:
            return _text_response("No SDK artifacts are currently published.")

        if sdk_name and sdk_name.strip():
            needle = sdk_name.strip().lower()
            matched = [p for p in sdks if needle in p.name.lower()]
            if not matched:
                available = ", ".join(p.name for p in sdks)
                return _text_response(
                    f"No SDK matching '{sdk_name}' was found. "
                    f"Available SDKs: {available}"
                )
            sdks = matched

        lines = ["=== PINE LABS SDK DOWNLOAD LINKS ==="]
        for p in sdks:
            size_kb = p.stat().st_size / 1024
            url = f"{base}/{p.name}"
            lines.append(f"- {p.name} ({size_kb:,.1f} KB)\n  {url}")
        return _text_response("\n".join(lines))
