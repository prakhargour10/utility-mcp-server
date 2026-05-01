# Model: `OperationState` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Lifecycle state of an operation tracked by `event_id`. Returned via `check_status`.

## Variants

| Name | Notes |
|---|---|
| `Pending` | SDK accepted the call but has not yet handed it to the transport. |
| `InFlight` | Transport accepted the call; awaiting the terminal reply. |
| `Completed` | Terminal returned success. `OperationStatus.result` is set. |
| `Failed` | Terminal returned failure or transport failed mid-stream. |
| `Cancelled` | Caller cancelled the op and it did not commit. |
| `Unknown` | SDK has no record of this `event_id`. Valid recovery answer. |

## Cross-references

`OperationStatus`, `apis/check_status`, `concepts/eventid-and-reconciliation`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
