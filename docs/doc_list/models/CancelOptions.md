# Model: `CancelOptions` (sealed / [Enum] interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Per-call transport-specific extras for `cancel`. v1 ships only the Cloud variant.

## Variants

| Name | Signature | Notes |
|---|---|---|
| `Cloud` | `Cloud(CloudCancelOptions options)` | Required when active transport is Cloud. |

## MUST

- Pass `null` for AppToApp / PADController (note: those raise `NotSupported` anyway in v1).
- Pass the `Cloud` variant only when active transport is Cloud.

## Cross-references

`CloudCancelOptions`, `apis/cancel`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
