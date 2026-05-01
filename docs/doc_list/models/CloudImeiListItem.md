# Model: `CloudImeiListItem` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

A single IMEI entry inside `CloudUploadImeiListOptions.imei_list`.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `imei` | `string` | yes | |
| `status` | `i32` | yes | Opaque status code understood by the upstream. |

## Cross-references

`CloudUploadImeiListOptions`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
