# Model: `TransactionType` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

The kind of terminal-side operation. v1 ships all six; individual transports may reject types they don't support.

## Variants

| Name | Notes |
|---|---|
| `Sale` | Standard charge. |
| `Refund` | Requires `original_event_id`. |
| `Void` | Requires `original_event_id`. |
| `PreAuth` | Pre-authorisation hold. |
| `Capture` | Capture against a prior PreAuth. Requires `original_event_id`. |
| `BalanceInquiry` | Card balance check. |

## MUST

- `original_event_id` is required for `Refund` / `Void` / `Capture`; rejected for `Sale` / `PreAuth` / `BalanceInquiry`.

## Cross-references

`TransactionRequest`, `apis/do_transaction`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
