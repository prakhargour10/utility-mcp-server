# Model: `DiscoveryListener` (callback)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Callback for discover_terminals. on_terminal_found may fire 0..N times.

## Methods

| Name | Signature | Notes |
|---|---|---|
| `on_terminal_found` | `void on_terminal_found(Terminal terminal)` | One per terminal. |
| `on_completed` | `void on_completed()` | Discovery ended cleanly. |
| `on_failure` | `void on_failure(SdkError error)` | Discovery aborted. |

## MUST

- Callbacks are serialised — no two callbacks fire concurrently on the same listener.
- Callbacks are NEVER fired on the caller's stack frame; they come from an SDK-internal worker thread.
- Marshal to the platform UI thread before touching UI elements.
- MUST NOT block in any callback.
- Exactly one of on_completed / on_failure ends the scan.

## MUST NOT

- Do not start a new discovery before on_completed/on_failure of the previous.

## Cross-references

`discover_terminals`, `Terminal`, `SdkError`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
