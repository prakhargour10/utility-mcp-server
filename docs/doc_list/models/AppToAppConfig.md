# Model: `AppToAppConfig` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Identity / wire config for the AppToApp transport. Required when `SdkConfig.transport == AppToApp`. `application_id` lives on `SdkConfig` (top-level), NOT here.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `user_id` | `string` | yes | Calling user id. Maps to upstream `Header.UserId`. |
| `version` | `string` | yes | Calling app version. Maps to upstream `Header.VersionNo`. In production this MUST equal `"1.0"`; other values are rejected by the upstream service. |

## MUST

- In production, `version` MUST be `"1.0"`.

## Cross-references

`SdkConfig`, `TransportType`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
