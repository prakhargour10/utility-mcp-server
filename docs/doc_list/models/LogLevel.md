# Model: `LogLevel` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Severity for the SDK's logger port.

## Values

| Value | Notes |
|---|---|
| `Trace` | Most verbose. |
| `Debug` | masked_pan and other low-sensitivity diagnostics may appear here. |
| `Info` | Default. |
| `Warn` | Recoverable anomalies. |
| `Error` | Failures. |
| `Off` | Disable all logging. |

## MUST

- Default to Info in production.

## MUST NOT

- Never log card data, PIN, full PAN, tokens, or keys at any level.

## Cross-references

`SdkConfig`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
