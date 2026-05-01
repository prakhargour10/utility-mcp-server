# Model: `TransactionListener` (callback)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Callback for do_transaction. Exactly one of on_success or on_failure fires per call.

## Methods

| Name | Signature | Notes |
|---|---|---|
| `on_started` | `void on_started(string event_id)` | Fires once with the SDK-allocated event_id. |
| `on_success` | `void on_success(TransactionResult result)` | Terminal-state success. |
| `on_failure` | `void on_failure(SdkError error)` | Terminal-state failure. |

## MUST

- Callbacks are serialised — no two callbacks fire concurrently on the same listener.
- Callbacks are NEVER fired on the caller's stack frame; they come from an SDK-internal worker thread.
- Marshal to the platform UI thread before touching UI elements.
- MUST NOT block in any callback.
- Disable trigger UI on on_started; re-enable on terminal-state callback.

## MUST NOT

- Do not call do_transaction again before on_success / on_failure.
- Do not assume on_started fired if do_transaction threw synchronously.

## Cross-references

`do_transaction`, `TransactionResult`, `SdkError`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
