# Model: `TransportOptions` (sealed / [Enum] interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Per-call transport-specific extras for `do_transaction`. The merchant supplies the variant matching the **active** transport. Mismatched variant raises `SdkError.InvalidInput` synchronously.

## Variants

| Name | Signature | Notes |
|---|---|---|
| `AppToApp` | `AppToApp(AppToAppTransactionOptions options)` | Optional NCMC / GST fields. |
| `Cloud` | `Cloud(CloudTransactionOptions options)` | **REQUIRED** on Cloud `do_transaction`. |
| `PadController` | `PadController(PadControllerTransactionOptions options)` | Loose key/value extras. |

## Cross-references

`AppToAppTransactionOptions`, `CloudTransactionOptions`, `PadControllerTransactionOptions`, `TransactionRequest`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
