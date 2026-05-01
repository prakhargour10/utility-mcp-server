# Model: `CloudUploadImeiListOptions` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Cloud admin call: register / refresh the IMEI list known to the upstream for a store. Routed through `upload_imei_list`.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `merchant_id` | `string` | yes | |
| `security_token` | `string` | yes | Never log. |
| `store_id` | `string` | yes | |
| `hardware_id` | `string?` | no | |
| `imei_list` | `sequence<CloudImeiListItem>` | yes | |

## Cross-references

`CloudImeiListItem`, `UploadImeiListResult`, `apis/upload_imei_list`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
