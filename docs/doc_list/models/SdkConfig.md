# Model: `SdkConfig` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

SDK-wide construction config. All fields optional; pass an empty SdkConfig for the most common case. Holds infrastructure config only — merchant identity belongs on TransactionRequest.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `default_timeout_ms` | `u32?` | no | Range 1_000..600_000. Default 60_000. |
| `log_level` | `LogLevel?` | no | Default Info. |
| `transport` | `TransportType?` | no | Initial transport. Null = no transport selected. |
| `app_to_app` | `AppToAppConfig?` | conditional | Required iff transport == AppToApp (or any later set_transport(AppToApp)). |
| `application_id` | `string?` | conditional | Pinelabs-provisioned. Required for AppToApp DoTxn (MethodId=1001). Forwarded as Header.ApplicationId. |
| `cloud` | `CloudConfig?` | conditional | Required iff transport == Cloud. |
| `pad_controller` | `PadControllerConfig?` | conditional | Honoured iff transport == PadController. |

## MUST

- Validate ranges yourself before calling — the SDK will throw InvalidInput otherwise.

## MUST NOT

- Do not put merchant_id, terminal_id, or credentials here.

## Cross-references

`AppToAppConfig`, `CloudConfig`, `PadControllerConfig`, `TransportType`, `LogLevel`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
