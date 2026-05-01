# Model: `TestPrintListener` (callback interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Callback for `test_print`. Same threading and ordering contract as `TransactionListener`.

## Methods

| Name | Signature | Notes |
|---|---|---|
| `on_started` | `on_started(string event_id)` | Fires once with the SDK-allocated event_id. |
| `on_success` | `on_success(string event_id)` | Print job completed at the terminal. |
| `on_failure` | `on_failure(SdkError error)` | |

## Cross-references

`apis/test_print`, `SdkError`, `concepts/threading`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
