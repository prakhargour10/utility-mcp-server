"""MCP tool for retrieving Pine Labs SDK download links."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

_SDK_EXTENSIONS = {".aar", ".jar", ".zip", ".tar.gz", ".tgz", ".whl"}


def _text_response(text: str) -> dict[str, Any]:
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


def register(mcp: FastMCP, sdk_dir: Path, download_base_url: str) -> None:
    """Register the SDK download tool on the FastMCP server."""

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
        """Return public download URL(s) for SDK artifacts in the sdk/ folder."""
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
