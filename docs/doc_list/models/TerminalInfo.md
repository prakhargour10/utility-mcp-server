# Model: `TerminalInfo` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Static / diagnostic info reported by the connected terminal. Returned by `get_terminal_info`.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `model` | `string?` | no | |
| `firmware_version` | `string?` | no | |
| `serial_number` | `string?` | no | |
| `battery_percent` | `u8?` | no | 0..100. Null if terminal does not report battery. |

## Cross-references

`apis/get_terminal_info`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
