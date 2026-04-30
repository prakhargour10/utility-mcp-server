# Model: `TransactionStatus` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Terminal-state outcome of a transaction.

## Values

| Value | Notes |
|---|---|
| `Success` | Terminal accepted and settled. |
| `Failed` | Terminal/transport reported failure. |
| `Pending` | Cloud-only: upload acknowledged but not yet settled. Drive next state via check_status. |

## MUST

- Treat Pending as not-yet-final on Cloud.

## MUST NOT

- Do not assume Pending will eventually become Success.

## Cross-references

`TransactionResult`, `check_status`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
