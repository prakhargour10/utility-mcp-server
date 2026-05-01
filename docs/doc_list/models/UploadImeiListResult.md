# Model: `UploadImeiListResult` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Result of `upload_imei_list`. `response_code` is the decimal-stringified upstream code; `response_message` is the upstream verbatim message when present.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `response_code` | `string` | yes | |
| `response_message` | `string?` | no | |

## Cross-references

`CloudUploadImeiListOptions`, `apis/upload_imei_list`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
