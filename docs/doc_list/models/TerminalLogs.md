# Model: `TerminalLogs` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Snapshot of terminal-side logs returned by `get_logs`.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `lines` | `sequence<string>` | yes | Raw lines as the terminal reported them. The SDK does not parse, redact, or sort. |

## MUST

- Treat lines as opaque diagnostic strings; never log to a destination that is not your secure log sink.

## Cross-references

`apis/get_logs`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
