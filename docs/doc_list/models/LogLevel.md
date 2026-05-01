# Model: `LogLevel` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Severity for the SDK's logger port. Maps to platform-native log levels in each binding.

## Variants

| Name | Notes |
|---|---|
| `Trace` | Most verbose. |
| `Debug` | Diagnostic. `masked_pan` is logged only at this level or below. |
| `Info` | Default. |
| `Warn` | Recoverable issues. |
| `Error` | Failures. |
| `Off` | No logging. |

## Cross-references

`SdkConfig`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
