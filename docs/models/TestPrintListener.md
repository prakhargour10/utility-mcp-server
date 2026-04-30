# Model: `TestPrintListener` (callback)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Callback for test_print. Same threading and ordering contract as TransactionListener.

## Methods

| Name | Signature | Notes |
|---|---|---|
| `on_started` | `void on_started(string event_id)` |  |
| `on_success` | `void on_success(string event_id)` | Carries the same event_id. |
| `on_failure` | `void on_failure(SdkError error)` |  |

## MUST

- Callbacks are serialised — no two callbacks fire concurrently on the same listener.
- Callbacks are NEVER fired on the caller's stack frame; they come from an SDK-internal worker thread.
- Marshal to the platform UI thread before touching UI elements.
- MUST NOT block in any callback.

## MUST NOT

_(no anti-patterns)_

## Cross-references

`test_print`, `SdkError`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
