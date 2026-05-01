# Model: `AppToAppConfig` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Identity / wire config for the AppToApp transport (MasterApp Messenger).

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `user_id` | `string` | yes | Maps to MasterApp Header.UserId. |
| `version` | `string` | yes | Maps to Header.VersionNo. In production MUST equal "1.0" (AppConstants.MASTERAPP_API_VERSION). Other values are rejected by MasterService. |

## MUST

- Set version = "1.0" in production.

## MUST NOT

- Do not put application_id here — it lives on SdkConfig.

## Cross-references

`SdkConfig`, `PlatformAppToAppBridge`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
