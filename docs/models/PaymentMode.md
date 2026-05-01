# Model: `PaymentMode` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Allowed payment instruments. Open set; explicitly IGNORED on Cloud (use TransportOptions.Cloud.allowed_payment_mode string instead).

## Values

| Value | Notes |
|---|---|
| `Card` |  |
| `Upi` |  |
| `Wallet` |  |
| `Bnpl` |  |
| `Emi` |  |
| `Cash` |  |

## MUST

- On Cloud transport, use the opaque string in CloudTransactionOptions.allowed_payment_mode.

## MUST NOT

- Do not assume the enum is exhaustive — new variants may appear in minor releases.

## Cross-references

`TransactionRequest`, `CloudTransactionOptions`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
