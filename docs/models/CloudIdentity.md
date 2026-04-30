# Model: `CloudIdentity` (sealed)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Per-call identity for Cloud calls. Two shapes.

## Variants

| Name | Signature | Notes |
|---|---|---|
| `Imei` | `Imei(string merchant_store_pos_code, string imei)` | Device identity anchored on IMEI. |
| `Store` | `Store(string store_id, string? client_id)` | Store-anchored identity. |

## MUST

- Choose one variant per call.

## MUST NOT

- Do not mix shapes.

## Cross-references

`CloudTransactionOptions`, `CloudCancelOptions`, `CloudCheckStatusOptions`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
