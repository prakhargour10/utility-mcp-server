# Model: `CloudCheckStatusOptions` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Cloud check_status extras. Required when active transport is Cloud.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `merchant_id` | `string` | yes | |
| `security_token` | `string` | yes | Never log. |
| `identity` | `CloudIdentity` | yes | |

## Cross-references

`CheckStatusOptions`, `CloudIdentity`, `apis/check_status`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
