"""
LLM Layer for the Campaign Recommendation POC.

Flow:
    User { hardware_id, description }
        -> server.list_campaigns_for_device(hardware_id)
              => shortlist of {campaign_id, description}
        -> Azure OpenAI (gpt-4o) picks the best campaign_id for the user's intent
        -> server.get_campaign(chosen_id) returns full campaign details
        -> Final response returned to caller
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from openai import AzureOpenAI

from server import get_campaign, list_campaigns_for_device

# ---------------------------------------------------------------------------
# Azure OpenAI setup
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

_client = AzureOpenAI(
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    http_client=httpx.Client(verify=False),
)


def call_ai(prompt: str, max_tokens: int = 200, temperature: float = 0.0) -> str:
    """Send a single-turn prompt to Azure OpenAI and return the text reply."""
    if not AZURE_API_KEY or not AZURE_ENDPOINT:
        raise RuntimeError("Azure OpenAI credentials missing — check your .env file.")

    print("\n" + "=" * 80)
    print(f"[LLM REQUEST] deployment={AZURE_DEPLOYMENT} temperature={temperature} max_tokens={max_tokens}")
    print("-" * 80)
    print(prompt)
    print("=" * 80)

    response = _client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=float(temperature),
        top_p=1.0,
    )
    reply = response.choices[0].message.content.strip()

    usage = getattr(response, "usage", None)
    print("\n" + "=" * 80)
    print("[LLM RESPONSE]" + (f" usage={usage}" if usage else ""))
    print("-" * 80)
    print(reply)
    print("=" * 80 + "\n")

    return reply


# ---------------------------------------------------------------------------
# Selection prompt
# ---------------------------------------------------------------------------

SELECTION_PROMPT = """You are a campaign-selection assistant.

The user has expressed a free-text intent. Below is a numbered list of campaigns
available for their device. Each line has a `campaign_id` and a short
`description` of the offer.

Pick the SINGLE campaign whose description best matches the user's intent.

Return ONLY a JSON object with EXACTLY these keys (no markdown, no commentary):
{{
  "campaign_id": "<one of the campaign_ids above, or empty string if none fit>",
  "reason": "<one short sentence explaining the choice>"
}}

User intent:
  {user_intent}

Available campaigns:
{shortlist_block}

JSON:"""


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


def _format_shortlist(shortlist: list[dict[str, Any]]) -> str:
    lines = []
    for item in shortlist:
        cid = item.get("campaign_id", "")
        desc = (item.get("description") or "").replace("\n", " ").strip()
        lines.append(f"- campaign_id: {cid}\n  description: {desc}")
    return "\n".join(lines) if lines else "(none)"


def _extract_campaign_id(reply: str, valid_ids: set[str]) -> tuple[str, str]:
    """Parse the LLM reply, returning (campaign_id, reason).

    Falls back to the first valid id-shaped token in the reply if JSON parsing fails.
    """
    cleaned = _strip_code_fences(reply)
    try:
        parsed = json.loads(cleaned)
        cid = str(parsed.get("campaign_id", "")).strip()
        reason = str(parsed.get("reason", "")).strip()
        if cid in valid_ids:
            return cid, reason
        return "", reason or "LLM returned an unknown campaign_id."
    except json.JSONDecodeError:
        # Last-ditch: regex hunt for any CMP-XXXX token that is in the valid set.
        for match in re.findall(r"CMP-\d{4}", reply):
            if match in valid_ids:
                return match, "Extracted from non-JSON reply."
        return "", "LLM returned non-JSON and no valid campaign_id was found."


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def recommend(model_name: str, description: str) -> dict[str, Any]:
    """Full pipeline: shortlist by model_name -> LLM picks -> return full details."""
    listing = list_campaigns_for_device(model_name=model_name)
    shortlist = listing.get("shortlist", [])

    # No campaigns at all for this device.
    if not shortlist:
        return {
            "model_name": model_name,
            "user_intent": description,
            "match_count": 0,
            "recommended_campaign": {},
            "note": "No matching campaign found.",
        }

    # Only one option — skip the LLM entirely.
    if len(shortlist) == 1:
        only_id = shortlist[0]["campaign_id"]
        return {
            "model_name": model_name,
            "user_intent": description,
            "match_count": 1,
            "recommended_campaign": get_campaign(only_id),
            "selection_reason": "Only one campaign available for this device.",
        }

    # Ask the LLM to pick the best fit.
    prompt = SELECTION_PROMPT.format(
        user_intent=description or "(no description supplied)",
        shortlist_block=_format_shortlist(shortlist),
    )
    reply = call_ai(prompt)

    valid_ids = {item["campaign_id"] for item in shortlist}
    chosen_id, reason = _extract_campaign_id(reply, valid_ids)

    # LLM said none of the shortlisted campaigns fit the user's intent.
    if not chosen_id:
        return {
            "model_name": model_name,
            "user_intent": description,
            "match_count": len(shortlist),
            "recommended_campaign": {},
            "note": "No matching campaign found.",
            "selection_reason": reason or "LLM did not pick any shortlisted campaign.",
        }

    return {
        "model_name": model_name,
        "user_intent": description,
        "match_count": len(shortlist),
        "recommended_campaign": get_campaign(chosen_id),
        "selection_reason": reason,
    }
