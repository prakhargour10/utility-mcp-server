# Model: `PadControllerTransactionOptions` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

PADController request extras placeholder. Loose key/value extras forwarded into the underlying CSV under their column names.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `extras` | `record<string,string>?` | no | Max 32 entries; values may contain neither `,` nor `\n`. |

## Cross-references

`TransportOptions`, `PadControllerConfig`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
