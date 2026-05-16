# Campaign Recommendation MCP (POC)

A lightweight Proof-of-Concept that recommends marketing campaigns for a given device using simple **rule-based matching** — no embeddings, no vector DB, no semantic search.

```
User Query  →  LLM Layer  →  MCP Tool  →  campaigns.json  →  Matched Campaigns
```

## Files

| File | Purpose |
| --- | --- |
| `campaigns.json` | Local "DB" — 20 dummy campaign records following the exact schema you provided, plus a `category` field. |
| `server.py` | MCP server exposing `recommend_campaigns` and `list_categories` tools. |
| `test_local.py` | Smoke test that invokes the matching logic directly (no MCP client needed). |
| `requirements.txt` | Just the `mcp` Python SDK. |

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the smoke test

```powershell
python test_local.py
```

## Run as an MCP server (stdio)

```powershell
python server.py
```

### VS Code MCP config (`.vscode/mcp.json` or user settings)

```jsonc
{
  "servers": {
    "campaign-recommendation": {
      "command": "python",
      "args": ["d:/AI Works/CampaignMCP/server.py"]
    }
  }
}
```

## Tool contract

### `recommend_campaigns`

**Input** (LLM extracts these from the user's natural-language request):

```json
{
  "hardware_id": "HW-123",
  "description": "I want a gaming laptop with RTX GPU",
  "category": "Gaming Laptop",
  "manufacturer": "ASUS",
  "model_name": "",
  "keywords": ["gaming", "rtx"],
  "top_k": 5,
  "only_active": true
}
```

**Output**:

```json
{
  "hardware_id": "HW-123",
  "match_count": 2,
  "recommended_campaigns": [
    {
      "campaign_name": "ROG Strix Diwali Blast",
      "manufacturer": "ASUS",
      "model_name": "ROG Strix G16",
      "description": "Flat 15% off on ASUS ROG Strix gaming laptops ...",
      "status": "active",
      "category": "Gaming Laptop"
    }
  ]
}
```

## Matching rules (scoring)

| Signal | Weight |
| --- | --- |
| Exact / substring category match | **50** |
| Token-level partial category match | 15 |
| Manufacturer match | 30 |
| Full model_name substring | 25 |
| Partial model_name token | 8 |
| Each keyword hit in `category + manufacturer + model + description + name` | 5 |
| Each description token hit | 2 |

Campaigns with score `0` are dropped. The remaining set is sorted descending and the top `top_k` returned. By default only `status == "active"` campaigns are considered.

## LLM layer responsibility

Your orchestrating LLM should:

1. Read the user's `{ hardware_id, description }`.
2. Extract `category`, `manufacturer`, `model_name`, and `keywords`.
3. Decide whether to call `recommend_campaigns`.
4. Pass the extracted filters as tool arguments.
5. Present the returned campaigns back to the user.

That's it — intentionally simple, demo-ready.
