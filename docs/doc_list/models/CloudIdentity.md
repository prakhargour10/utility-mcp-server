# Model: `CloudIdentity` (sealed / [Enum] interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Per-call identity for Cloud calls. Two shapes: an IMEI-anchored device identity, or a store-anchored identity with an optional client id.

## Variants

| Name | Signature | Notes |
|---|---|---|
| `Imei` | `Imei(string merchant_store_pos_code, string imei)` | Device identity. |
| `Store` | `Store(string store_id, string? client_id)` | Store-anchored identity. |

## Cross-references

`CloudTransactionOptions`, `CloudCancelOptions`, `CloudCheckStatusOptions`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
