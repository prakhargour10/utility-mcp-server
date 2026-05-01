# Model: `TransactionStatus` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Terminal-state outcome of a transaction.

## Variants

| Name | Notes |
|---|---|
| `Success` | Terminal acknowledged success. |
| `Failed` | Terminal returned non-success. |
| `Pending` | **Cloud only.** `do_transaction` returns once upload is acknowledged; merchant drives subsequent state via `check_status`. |

## Cross-references

`TransactionResult`, `apis/check_status`, `OperationState`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
