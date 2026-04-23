"""
MCP Server with FastAPI
Tools: get_current_time, get_current_date, get_share_price,
       list_pinelabs_apis, get_api_documentation
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yfinance as yf
from mcp.server.fastmcp import FastMCP

IST = ZoneInfo("Asia/Kolkata")
DOCS_ROOT: Path = Path(__file__).parent / "api-docs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("utility-mcp-server")

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
    """Scan DOCS_ROOT and return mapping of apiName -> markdown file path."""
    if not DOCS_ROOT.exists():
        return {}
    apis: dict[str, Path] = {}
    for md_file in DOCS_ROOT.rglob("*.md"):
        if md_file.stem not in apis:
            apis[md_file.stem] = md_file
    return apis


# ---------------------------------------------------------------------------
# Time & Date tools
# ---------------------------------------------------------------------------
@mcp.tool()
def get_current_time() -> str:
    """Returns the current time in IST (Indian Standard Time)."""
    now = datetime.now(IST)
    return now.strftime("%I:%M:%S %p IST")


@mcp.tool()
def get_current_date() -> str:
    """Returns the current date in IST (Indian Standard Time)."""
    now = datetime.now(IST)
    return now.strftime("%A, %d %B %Y")


# ---------------------------------------------------------------------------
# Stock price tool
# ---------------------------------------------------------------------------
@mcp.tool()
def get_share_price(company_name: str) -> str:
    """
    Returns the latest share price of a company by its name.

    Args:
        company_name: The name of the company (e.g. 'Pine Labs', 'Infosys', 'Apple')
    """
    try:
        results = yf.Search(company_name, max_results=5)
        quotes = results.quotes
        if not quotes:
            return f"Could not find any ticker for '{company_name}'. Try a more specific name."

        ticker_symbol = quotes[0].get("symbol", "")
        short_name = quotes[0].get("shortname") or quotes[0].get("longname") or ticker_symbol
        exchange = quotes[0].get("exchange", "")

        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info
        price = info.last_price
        currency = getattr(info, "currency", "USD") or "USD"

        if price is None:
            return f"Price data unavailable for '{short_name}' ({ticker_symbol})."

        return (
            f"Company   : {short_name}\n"
            f"Ticker    : {ticker_symbol} ({exchange})\n"
            f"Price     : {currency} {price:,.2f}\n"
            f"As of     : {datetime.now(IST).strftime('%d %b %Y, %I:%M %p IST')}"
        )
    except Exception as e:
        return f"Error fetching share price for '{company_name}': {str(e)}"


# ---------------------------------------------------------------------------
# Pine Labs SDK documentation tools
# ---------------------------------------------------------------------------
@mcp.tool(
    name="list_pinelabs_apis",
    description=(
        "List all available Pine Labs SDK APIs grouped by category "
        "(e.g. 'transaction/doTransaction'). Call this first to discover "
        "valid api_name values for 'get_api_documentation'."
    ),
)
async def list_pinelabs_apis() -> dict[str, Any]:
    """Return all available Pine Labs SDK API names grouped by category."""
    apis = _discover_apis()
    if not apis:
        return {"content": [{"type": "text", "text": "No API docs found."}]}
    listing = sorted(f"{p.parent.name}/{n}" for n, p in apis.items())
    logger.info("list_pinelabs_apis returning %d entries", len(listing))
    return {"content": [{"type": "text", "text": "\n".join(listing)}]}


@mcp.tool(
    name="get_api_documentation",
    description=(
        "Fetch Pine Labs SDK documentation for a specific API. "
        "Use 'list_pinelabs_apis' first to discover available api_name values."
    ),
)
async def get_api_documentation(api_name: str) -> dict[str, Any]:
    """Return the markdown documentation for the given Pine Labs SDK API."""
    if not api_name or not api_name.strip():
        return {"content": [{"type": "text", "text": "Error: 'api_name' is required."}]}
    apis = _discover_apis()
    md_path = apis.get(api_name)
    if md_path is None:
        available = ", ".join(sorted(apis)) or "none"
        return {"content": [{"type": "text", "text": f"API '{api_name}' not found. Available: {available}"}]}
    try:
        doc = md_path.read_text(encoding="utf-8")
        logger.info("Returning docs for '%s' (%d chars)", api_name, len(doc))
        return {"content": [{"type": "text", "text": doc}]}
    except OSError as exc:
        return {"content": [{"type": "text", "text": f"Error reading docs for '{api_name}': {exc}"}]}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

