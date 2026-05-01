# Model: `DiscoveryListener` (callback interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Callback for `discover_terminals`. `on_terminal_found` may fire 0..N times. Exactly one terminal-state callback (`on_completed` or `on_failure`) fires per discovery.

## Methods

| Name | Signature |
|---|---|
| `on_terminal_found` | `on_terminal_found(Terminal terminal)` |
| `on_completed` | `on_completed()` |
| `on_failure` | `on_failure(SdkError error)` |

## Cross-references

`Terminal`, `apis/discover_terminals`, `concepts/threading`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
