# Model: `TransportOptions` (sealed)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Per-call extras for do_transaction. Variant MUST match active transport.

## Variants

| Name | Signature | Notes |
|---|---|---|
| `AppToApp` | `AppToApp(AppToAppTransactionOptions)` | NCMC + GST extras. |
| `Cloud` | `Cloud(CloudTransactionOptions)` | REQUIRED on Cloud. |
| `PadController` | `PadController(PadControllerTransactionOptions)` | Loose key/value extras for now. |

## MUST

- Pick the variant matching the active transport at call time.

## MUST NOT

- Do not pass Cloud variant on AppToApp etc. — InvalidInput synchronously.

## Cross-references

`TransactionRequest`, `AppToAppTransactionOptions`, `CloudTransactionOptions`, `PadControllerTransactionOptions`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
