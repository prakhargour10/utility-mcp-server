"""
Campaign Recommendation MCP Server (POC)

New flow:
    1. Shortlist all campaigns whose `model_name` exactly matches the request.
    2. Hand the LLM ONLY {campaign_id, description} pairs.
    3. The LLM picks the best campaign_id for the user's intent.
    4. Caller looks the chosen campaign_id back up here for full details.

Tools exposed:
    - list_campaigns_for_device(model_name) -> shortlist of {campaign_id, description}
    - get_campaign(campaign_id)             -> full formatted campaign record
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CAMPAIGNS_FILE = BASE_DIR / "campaigns.json"

mcp = FastMCP("campaign-recommendation-mcp")


def _load_campaigns() -> list[dict[str, Any]]:
    """Load campaigns and assign a deterministic campaign_id derived from index."""
    with CAMPAIGNS_FILE.open("r", encoding="utf-8") as fh:
        records = json.load(fh)
    for idx, rec in enumerate(records, start=1):
        rec.setdefault("campaign_id", f"CMP-{idx:04d}")
    return records


def _format_campaign(c: dict[str, Any]) -> dict[str, Any]:
    """Trim a campaign record to the response shape returned to the caller."""
    raw_id = c.get("_id") or {}
    mongo_id = raw_id.get("$oid") if isinstance(raw_id, dict) else str(raw_id)
    return {
        "campaign_id": c.get("campaign_id", ""),
        "mongo_id": mongo_id or "",
        "campaign_name": c.get("campaign_name", ""),
        "hardware_id": c.get("hardware_id", ""),
        "manufacturer": c.get("manufacturer", ""),
        "model_name": c.get("model_name", ""),
        "category": c.get("category", ""),
        "description": c.get("description", ""),
        "status": c.get("status", ""),
        "start_date": c.get("start_date", ""),
        "end_date": c.get("end_date", ""),
        "s3_objects": c.get("s3_objects", []),
    }


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_campaigns_for_device(
    model_name: str,
    only_active: bool = True,
) -> dict[str, Any]:
    """Return a shortlist of campaigns for the given model_name.

    Each entry contains only `campaign_id` and `description` — exactly what the
    LLM needs to pick the best intent match. Filters strictly on exact
    (case-insensitive) model_name equality.
    """
    if not model_name:
        return {"model_name": "", "shortlist": []}

    mn = model_name.lower().strip()
    campaigns = _load_campaigns()

    shortlist = [
        {"campaign_id": c["campaign_id"], "description": c.get("description", "")}
        for c in campaigns
        if (c.get("model_name") or "").lower() == mn
        and (not only_active or (c.get("status") or "").lower() == "active")
    ]

    return {"model_name": model_name, "shortlist": shortlist}


@mcp.tool()
def get_campaign(campaign_id: str) -> dict[str, Any]:
    """Look up a single campaign's full details by campaign_id."""
    if not campaign_id:
        return {}
    cid = campaign_id.strip()
    for c in _load_campaigns():
        if c.get("campaign_id") == cid:
            return _format_campaign(c)
    return {}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        # Serve over HTTP at http://<host>:<port>/mcp
        mcp.settings.host = os.environ.get("MCP_HOST", "0.0.0.0")
        mcp.settings.port = int(os.environ.get("MCP_PORT", "8000"))
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
