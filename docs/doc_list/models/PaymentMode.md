# Model: `PaymentMode` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Allowed payment instruments for a `TransactionRequest`. **Open set in v1** — additional variants will be added.

## Variants

| Name | Notes |
|---|---|
| `Card` | Credit / debit card. |
| `Upi` | UPI. |
| `Wallet` | Digital wallet. |
| `Bnpl` | Buy-Now-Pay-Later. |
| `Emi` | EMI on card. |
| `Cash` | Cash. |

## MUST

- Generated `when` / `switch` MUST include a default arm — this is an open enum.

## MUST NOT

- Do not use this on the Cloud transport — it is **explicitly ignored on Cloud in v1**. Use `CloudTransactionOptions.allowed_payment_mode` (opaque string) instead.

## Cross-references

`TransactionRequest`, `CloudTransactionOptions`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
