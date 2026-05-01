# Model: `TerminalInfo` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Static / diagnostic info about the connected terminal.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `model` | `string?` | - |  |
| `firmware_version` | `string?` | - |  |
| `serial_number` | `string?` | - |  |
| `battery_percent` | `u8?` | - | 0..100. Null if not reported. |

## MUST

_(no positive obligations)_

## MUST NOT

_(no anti-patterns)_

## Cross-references

`get_terminal_info`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
