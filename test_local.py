"""
Quick local smoke test for the matching logic — does NOT start the MCP server.
Run:   python test_local.py
"""
from server import recommend_campaigns, list_categories
import json

print("Categories:", json.dumps(list_categories(), indent=2))

cases = [
    {
        "hardware_id": "HW-123",
        "description": "I want a powerful gaming laptop with RTX GPU",
        "category": "Gaming Laptop",
        "manufacturer": "",
        "model_name": "",
        "keywords": ["gaming", "rtx"],
    },
    {
        "hardware_id": "HW-456",
        "description": "Looking for a MacBook for college",
        "category": "MacBook",
        "manufacturer": "Apple",
        "model_name": "",
        "keywords": ["student"],
    },
    {
        "hardware_id": "HW-789",
        "description": "Need a split AC for summer",
        "category": "Air Conditioner",
        "manufacturer": "LG",
        "model_name": "",
        "keywords": ["summer", "cooling"],
    },
    {
        "hardware_id": "HW-999",
        "description": "Wireless earbuds with noise cancellation",
        "category": "Earbuds",
        "manufacturer": "",
        "model_name": "",
        "keywords": ["noise", "cancelling", "wireless"],
    },
]

for case in cases:
    print("\n=== Query ===")
    print(json.dumps(case, indent=2))
    print("--- Result ---")
    print(json.dumps(recommend_campaigns(**case, top_k=3), indent=2))
