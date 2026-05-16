"""
Thin async HTTP client around the 3 Pine Labs TMS endpoints used by the
campaign push pipeline:

  1. POST /v1/marketplace-processor/group/resources   -> create resource group
  2. POST /v1/marketplace-processor/group/terminals   -> create terminal group
  3. POST /v1/marketplace-processor/group/push-task   -> trigger MQTT push

All config (base URL, bearer token, client-id, created_by) is read from .env.
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

TMS_BASE_URL = os.getenv("TMS_BASE_URL", "https://api.tms.uat.pinelabs.com").rstrip("/")
TMS_BEARER_TOKEN = os.getenv("TMS_BEARER_TOKEN", "")
TMS_CLIENT_ID = os.getenv("TMS_CLIENT_ID", "")
TMS_CREATED_BY = os.getenv("TMS_CREATED_BY", "CampaignMCP")
TMS_TIMEOUT_SECONDS = float(os.getenv("TMS_TIMEOUT_SECONDS", "30"))

logger = logging.getLogger("tms_client")


class TMSError(RuntimeError):
    """Raised when a TMS API call returns a non-2xx response."""


def _headers() -> dict[str, str]:
    if not TMS_BEARER_TOKEN or TMS_BEARER_TOKEN == "PASTE_BEARER_TOKEN_HERE":
        raise TMSError("TMS_BEARER_TOKEN is not set in .env")
    token = TMS_BEARER_TOKEN.strip()
    if not token.lower().startswith("bearer "):
        token = f"Bearer {token}"
    sid = str(uuid.uuid4())
    tab = str(uuid.uuid4())
    return {
        "accept": "*/*",
        "content-type": "application/json",
        "authorization": token,
        "client-id": TMS_CLIENT_ID,
        "origin": "https://portal.tms.uat.pinelabs.com",
        "referer": "https://portal.tms.uat.pinelabs.com/",
        "user-agent": "CampaignMCP/1.0",
        "x-tms-session-id": sid,
        "x-tms-tab-id": tab,
    }


def _extract_id(payload: Any, candidate_keys: list[str]) -> int | str | None:
    """Best-effort extraction of an id from a TMS response body."""
    if not isinstance(payload, dict):
        return None
    for key in candidate_keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    data = payload.get("data")
    if isinstance(data, dict):
        for key in candidate_keys:
            if key in data and data[key] not in (None, ""):
                return data[key]
    if isinstance(data, list) and data and isinstance(data[0], dict):
        for key in candidate_keys:
            if key in data[0] and data[0][key] not in (None, ""):
                return data[0][key]
    return None


async def _post(client: httpx.AsyncClient, path: str, body: dict[str, Any], step: str, request_id: str) -> dict[str, Any]:
    url = f"{TMS_BASE_URL}{path}"
    started = time.perf_counter()
    logger.info("[%s] %s -> POST %s body=%s", request_id, step, url, body)
    try:
        resp = await client.post(url, json=body, headers=_headers(), timeout=TMS_TIMEOUT_SECONDS)
    except httpx.HTTPError as exc:
        logger.exception("[%s] %s network error: %s", request_id, step, exc)
        raise TMSError(f"{step} network error: {exc}") from exc

    duration_ms = int((time.perf_counter() - started) * 1000)
    text = resp.text
    try:
        payload = resp.json()
    except ValueError:
        payload = {"raw": text}

    logger.info(
        "[%s] %s <- status=%s duration_ms=%s body=%s",
        request_id, step, resp.status_code, duration_ms, payload,
    )

    if resp.status_code >= 400:
        raise TMSError(f"{step} failed status={resp.status_code} body={text[:500]}")
    return payload


async def create_resource_group(
    client: httpx.AsyncClient,
    *,
    request_id: str,
    mongo_campaign_id: str,
    model_name: str,
    manufacturer: str,
) -> int | str:
    body = {
        "created_by": TMS_CREATED_BY,
        "campaigns": [
            {
                "campaign_id": mongo_campaign_id,
                "model_name": model_name,
                "manufacturer": manufacturer,
            }
        ],
        "type": "campaign",
    }
    payload = await _post(client, "/v1/marketplace-processor/group/resources", body, "create_resource_group", request_id)
    rid = _extract_id(payload, ["resource_group_mapping_id", "id"])
    if rid is None:
        raise TMSError(f"create_resource_group: could not extract resource_group_mapping_id from {payload}")
    logger.info("[%s] create_resource_group extracted resource_group_mapping_id=%s", request_id, rid)
    return rid


async def create_terminal_group(
    client: httpx.AsyncClient,
    *,
    request_id: str,
    hardware_id: str,
) -> int | str:
    body = {
        "name": f"PushApp-{int(time.time() * 1000)}",
        "terminal_ids": [hardware_id],
        "created_by": TMS_CREATED_BY,
    }
    payload = await _post(client, "/v1/marketplace-processor/group/terminals", body, "create_terminal_group", request_id)
    tid = _extract_id(payload, ["terminal_group_mapping_id", "id"])
    if tid is None:
        raise TMSError(f"create_terminal_group: could not extract terminal_group_mapping_id from {payload}")
    logger.info("[%s] create_terminal_group extracted terminal_group_mapping_id=%s", request_id, tid)
    return tid


async def trigger_push_task(
    client: httpx.AsyncClient,
    *,
    request_id: str,
    resource_group_mapping_id: int | str,
    terminal_group_mapping_id: int | str,
) -> dict[str, Any]:
    body = {
        "resource_group_mapping_id": resource_group_mapping_id,
        "terminal_group_mapping_id": terminal_group_mapping_id,
        "push_type": "normal",
        "request_type": "instant",
        "created_by": TMS_CREATED_BY,
        "action_type": "campaign",
    }
    return await _post(client, "/v1/marketplace-processor/group/push-task", body, "trigger_push_task", request_id)
