# Model: `OperationState` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Lifecycle state returned by check_status.

## Values

| Value | Notes |
|---|---|
| `Pending` | SDK accepted, not yet handed to transport. |
| `InFlight` | Transport accepted; awaiting terminal. |
| `Completed` | Terminal returned success; OperationStatus.result set. |
| `Failed` | Terminal failure or transport mid-stream failure. |
| `Cancelled` | Caller cancelled and op did not commit. |
| `Unknown` | SDK has no record of this event_id (process restart, or id never allocated here). |

## MUST

- Treat Unknown as a valid recovery answer, not an error.

## MUST NOT

_(no anti-patterns)_

## Cross-references

`OperationStatus`, `check_status`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
