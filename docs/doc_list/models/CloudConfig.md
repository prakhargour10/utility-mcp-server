# Model: `CloudConfig` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Cloud transport configuration. Required when `SdkConfig.transport == Cloud`.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `type` | `CloudType` | yes | Single variant in v1: `CloudType.Ism`. |
| `base_url` | `string` | yes | Must parse as `https://...` with a host and no path/query/fragment. |
| `connect_timeout_ms` | `u32?` | no | Default 5_000. |
| `read_timeout_ms` | `u32?` | no | Default 245_000. Floor 1_000. |

## MUST

- `base_url` is strictly validated — `http://` or any path component raises `InvalidInput`.

## Cross-references

`SdkConfig`, `CloudType`, `CloudIdentity`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
