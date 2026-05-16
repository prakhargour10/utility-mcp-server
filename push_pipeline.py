"""
Fire-and-forget orchestrator that takes a matched campaign + hardware_id and
pushes it to a terminal via the 3-step TMS flow.

Each step is logged. Errors are caught and logged, never re-raised, so the
caller's request thread is never affected.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from tms_client import (
    TMSError,
    create_resource_group,
    create_terminal_group,
    trigger_push_task,
)

logger = logging.getLogger("push_pipeline")


async def push_campaign_to_terminal(
    *,
    request_id: str,
    hardware_id: str,
    campaign: dict[str, Any],
) -> None:
    """Run the 3-step TMS push flow asynchronously. Never raises."""
    campaign_id = campaign.get("campaign_id", "")
    mongo_id = campaign.get("mongo_id", "")
    model_name = campaign.get("model_name", "")
    manufacturer = campaign.get("manufacturer", "")

    logger.info(
        "[%s] push start hardware_id=%s campaign_id=%s mongo_id=%s model=%s manuf=%s",
        request_id, hardware_id, campaign_id, mongo_id, model_name, manufacturer,
    )

    if not (hardware_id and mongo_id and model_name and manufacturer):
        logger.error(
            "[%s] push aborted - missing required fields (hardware_id/mongo_id/model_name/manufacturer)",
            request_id,
        )
        return

    try:
        async with httpx.AsyncClient(verify=False) as client:
            resource_group_id = await create_resource_group(
                client,
                request_id=request_id,
                mongo_campaign_id=mongo_id,
                model_name=model_name,
                manufacturer=manufacturer,
            )
            terminal_group_id = await create_terminal_group(
                client,
                request_id=request_id,
                hardware_id=hardware_id,
            )
            push_response = await trigger_push_task(
                client,
                request_id=request_id,
                resource_group_mapping_id=resource_group_id,
                terminal_group_mapping_id=terminal_group_id,
            )
        logger.info(
            "[%s] push success hardware_id=%s campaign_id=%s push_response=%s",
            request_id, hardware_id, campaign_id, push_response,
        )
    except TMSError as exc:
        logger.error("[%s] push failed: %s", request_id, exc)
    except Exception as exc:
        logger.exception("[%s] push crashed: %s", request_id, exc)
