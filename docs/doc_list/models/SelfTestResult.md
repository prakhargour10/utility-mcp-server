# Model: `SelfTestResult` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Outcome of `run_self_test`.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `passed` | `boolean` | yes | |
| `details` | `sequence<string>` | yes | Raw terminal-reported result lines. |

## Cross-references

`apis/run_self_test`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
