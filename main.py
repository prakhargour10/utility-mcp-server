"""
MCP Server with FastAPI
Tools: get_current_time, get_current_date, get_share_price
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import yfinance as yf
from mcp.server.fastmcp import FastMCP

IST = ZoneInfo("Asia/Kolkata")

mcp = FastMCP(
    name="utility-mcp-server",
    instructions="A utility MCP server providing time, date, and stock price tools.",
)


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


@mcp.tool()
def get_share_price(company_name: str) -> str:
    """
    Returns the latest share price of a company by its name.

    Args:
        company_name: The name of the company (e.g. 'Pine Labs', 'Infosys', 'Apple')
    """
    try:
        # Search for the ticker symbol using yfinance
        results = yf.Search(company_name, max_results=5)
        quotes = results.quotes

        if not quotes:
            return f"Could not find any ticker for '{company_name}'. Try a more specific name."

        # Pick the best match (first result)
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


if __name__ == "__main__":
    mcp.run(transport="stdio")
