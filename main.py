"""
MCP Server with FastAPI (Streamable HTTP)
Tools: get_current_time, get_current_date, get_share_price,
       list_pinelabs_apis, get_api_documentation
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yfinance as yf
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
IST = ZoneInfo("Asia/Kolkata")
DOCS_ROOT: Path = Path(__file__).parent / "api-docs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("utility-mcp-server")

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="utility-mcp-server",
    instructions=(
        "A utility MCP server providing IST time, date, stock prices, "
        "and Pine Labs SDK API documentation."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _discover_apis() -> dict[str, Path]:
    if not DOCS_ROOT.exists():
        return {}
    apis: dict[str, Path] = {}
    for md_file in DOCS_ROOT.rglob("*.md"):
        if md_file.stem not in apis:
            apis[md_file.stem] = md_file
    return apis


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@mcp.tool()
def get_current_time() -> str:
    now = datetime.now(IST)
    return now.strftime("%I:%M:%S %p IST")


@mcp.tool()
def get_current_date() -> str:
    now = datetime.now(IST)
    return now.strftime("%A, %d %B %Y")


@mcp.tool()
def get_share_price(company_name: str) -> str:
    try:
        results = yf.Search(company_name, max_results=5)
        quotes = results.quotes

        if not quotes:
            return f"Could not find any ticker for '{company_name}'."

        ticker_symbol = quotes[0].get("symbol", "")
        short_name = quotes[0].get("shortname") or ticker_symbol

        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info

        price = info.last_price
        currency = getattr(info, "currency", "USD") or "USD"

        if price is None:
            return f"Price data unavailable for '{short_name}'."

        return (
            f"{short_name} ({ticker_symbol})\n"
            f"{currency} {price:,.2f}\n"
            f"{datetime.now(IST).strftime('%d %b %Y, %I:%M %p IST')}"
        )

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(name="list_pinelabs_apis")
async def list_pinelabs_apis() -> dict[str, Any]:
    apis = _discover_apis()

    if not apis:
        return {"content": [{"type": "text", "text": "No API docs found"}]}

    listing = sorted(f"{p.parent.name}/{n}" for n, p in apis.items())
    return {"content": [{"type": "text", "text": "\n".join(listing)}]}


@mcp.tool(name="get_api_documentation")
async def get_api_documentation(api_name: str) -> dict[str, Any]:
    apis = _discover_apis()

    md_path = apis.get(api_name)

    if md_path is None:
        return {"content": [{"type": "text", "text": "API not found"}]}

    try:
        doc = md_path.read_text(encoding="utf-8")
        return {"content": [{"type": "text", "text": doc}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": str(e)}]}


# ---------------------------------------------------------------------------
# ASGI app — used by uvicorn directly (endpoint: /mcp)
# ---------------------------------------------------------------------------
app = mcp.streamable_http_app()


# ---------------------------------------------------------------------------
# Run (for local dev only)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)