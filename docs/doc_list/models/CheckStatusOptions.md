# Model: `CheckStatusOptions` (sealed / [Enum] interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Per-call transport-specific extras for `check_status`. v1 ships only the Cloud variant.

## Variants

| Name | Signature | Notes |
|---|---|---|
| `Cloud` | `Cloud(CloudCheckStatusOptions options)` | Required when active transport is Cloud. |

## Cross-references

`CloudCheckStatusOptions`, `apis/check_status`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
