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


async def _recommend_and_push_job(
    *,
    request_id: str,
    hardware_id: str,
    model_name: str,
    description: str,
) -> None:
    """Background job: run LLM recommend + TMS push. Never raises."""
    job_logger = logging.getLogger("api.recommend_and_push.bg")
    job_logger.info(
        "[%s] bg start hardware_id=%s model=%s",
        request_id, hardware_id, model_name,
    )

    try:
        result = recommend(model_name=model_name, description=description)
    except Exception as exc:
        job_logger.exception("[%s] recommend failed: %s", request_id, exc)
        return

    campaign = result.get("recommended_campaign") or {}
    campaign_id = campaign.get("campaign_id", "")

    if not campaign_id:
        job_logger.info(
            "[%s] no relevant campaign found hardware_id=%s model=%s reason=%s",
            request_id, hardware_id, model_name,
            result.get("selection_reason", ""),
        )
        return

    job_logger.info(
        "[%s] campaign matched campaign_id=%s mongo_id=%s reason=%s",
        request_id, campaign_id, campaign.get("mongo_id", ""),
        result.get("selection_reason", ""),
    )

    await push_campaign_to_terminal(
        request_id=request_id,
        hardware_id=hardware_id,
        campaign=campaign,
    )


@app.post("/recommend-and-push")
def recommend_and_push_endpoint(
    req: RecommendAndPushRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Acknowledge instantly; run LLM recommend + TMS push in the background.

    Returns the moment the request is received. The LLM selection and the
    3-step TMS push (resource group -> terminal group -> push-task) both run
    in the background; results are visible in server logs only (keyed by
    request_id).
    """
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    logger = logging.getLogger("api.recommend_and_push")

    logger.info(
        "[%s] request received hardware_id=%s model=%s",
        request_id, req.hardware_id, req.model_name,
    )

    background_tasks.add_task(
        _recommend_and_push_job,
        request_id=request_id,
        hardware_id=req.hardware_id,
        model_name=req.model_name,
        description=req.description,
    )

    return {
        "request_id": request_id,
        "status": "queued",
        "message": "Request accepted. Recommendation and push are running in the background.",
    }

