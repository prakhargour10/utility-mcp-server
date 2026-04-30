# Model: `CloudConfig` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Cloud transport configuration. base_url MUST be a fully-qualified https:// URL with a host and no path/query/fragment.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `type` | `CloudType` | yes | Always Ism in v1. |
| `base_url` | `string` | yes | https://… host only. |
| `connect_timeout_ms` | `u32?` | no | Default 5_000. |
| `read_timeout_ms` | `u32?` | no | Default 245_000. Floor 1_000. |

## MUST

- Use https only. Validate base_url is a host with no path.

## MUST NOT

- Do not embed credentials in base_url.

## Cross-references

`CloudType`, `SdkConfig`, `CloudIdentity`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
