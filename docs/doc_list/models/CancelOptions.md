# Model: `CancelOptions` (sealed)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Per-call extras for cancel.

## Variants

| Name | Signature | Notes |
|---|---|---|
| `Cloud` | `Cloud(CloudCancelOptions)` | REQUIRED on Cloud transport. |

## MUST

- Use Cloud variant when active transport is Cloud; pass null otherwise.

## MUST NOT

- Do not pass on non-Cloud transports — InvalidInput.

## Cross-references

`cancel`, `CloudCancelOptions`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
