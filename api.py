"""
FastAPI wrapper around the Campaign Recommendation pipeline.

Exposes:
    POST /recommend           -> shortlist by model_name, LLM picks best, full details returned
    POST /recommend-and-push  -> recommend + asynchronously push the chosen campaign to a terminal via TMS
    GET  /shortlist           -> raw shortlist for a model_name (no LLM)
    GET  /health              -> health check

Run:
    uvicorn api:app --reload --port 8000
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

from llm_layer import recommend
from push_pipeline import push_campaign_to_terminal
from server import list_campaigns_for_device

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="Campaign Recommendation API",
    description="POC API that recommends a marketing campaign for a given POS device.",
    version="0.3.0",
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RecommendRequest(BaseModel):
    model_name: str = Field(..., description="Exact device model name, e.g. 'A910', 'V240M'.")
    description: str = Field(default="", description="Free-text user request / intent.")


class RecommendAndPushRequest(BaseModel):
    hardware_id: str = Field(..., description="Terminal id, e.g. '0821396392'.")
    model_name: str = Field(..., description="Exact device model name, e.g. 'A920'.")
    description: str = Field(default="", description="Free-text user intent for campaign matching.")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/shortlist")
def shortlist(model_name: str) -> dict[str, Any]:
    """Return the raw shortlist of campaigns for a model_name (no LLM call)."""
    return list_campaigns_for_device(model_name=model_name)


@app.post("/recommend")
def recommend_endpoint(req: RecommendRequest) -> dict[str, Any]:
    """Shortlist by model_name, ask LLM to pick best match, return full campaign."""
    try:
        return recommend(model_name=req.model_name, description=req.description)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/recommend-and-push")
def recommend_and_push_endpoint(
    req: RecommendAndPushRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Recommend a campaign and asynchronously push it to the terminal via TMS.

    Returns immediately. The 3-step TMS push (resource group -> terminal group ->
    push-task) runs in the background; results are visible in server logs only.
    """
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    logger = logging.getLogger("api.recommend_and_push")

    try:
        result = recommend(model_name=req.model_name, description=req.description)
    except Exception as exc:
        logger.exception("[%s] recommend failed: %s", request_id, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    campaign = result.get("recommended_campaign") or {}
    campaign_id = campaign.get("campaign_id", "")

    if not campaign_id:
        logger.info(
            "[%s] no relevant campaign found hardware_id=%s model=%s",
            request_id, req.hardware_id, req.model_name,
        )
        return {
            "request_id": request_id,
            "campaign_found": False,
            "message": "No relevant campaign found",
            "selection_reason": result.get("selection_reason", ""),
        }

    # Schedule async push; never blocks the response.
    background_tasks.add_task(
        push_campaign_to_terminal,
        request_id=request_id,
        hardware_id=req.hardware_id,
        campaign=campaign,
    )

    logger.info(
        "[%s] queued push hardware_id=%s campaign_id=%s mongo_id=%s",
        request_id, req.hardware_id, campaign_id, campaign.get("mongo_id", ""),
    )

    return {
        "request_id": request_id,
        "campaign_found": True,
        "campaign_id": campaign_id,
        "campaign_name": campaign.get("campaign_name", ""),
        "message": "Campaign matched. MQTT push dispatched asynchronously.",
        "push_status": "queued",
        "selection_reason": result.get("selection_reason", ""),
    }

