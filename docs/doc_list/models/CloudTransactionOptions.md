# Model: `CloudTransactionOptions` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Cloud REST request extras. **REQUIRED** on every Cloud `do_transaction`.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `merchant_id` | `string` | yes | |
| `security_token` | `string` | yes | Per-call token; never log. |
| `identity` | `CloudIdentity` | yes | |
| `transaction_number` | `string` | yes | Merchant idempotency key. |
| `sequence_number` | `string` | yes | Merchant-supplied. |
| `allowed_payment_mode` | `string` | yes | Opaque pass-through. Common observed value: `"10"`. |
| `total_invoice_amount` | `string` | yes | Validated `^[0-9]+$`. |
| `txn_type` | `i32` | yes | Opaque transaction-type code. |
| `original_plutus_transaction_reference_id` | `string?` | no | Reference to original `PlutusTransactionReferenceID` for refund-style chained transactions. |
| `auto_cancel_duration_minutes` | `u32` | yes | Validated 1..=1440. |

## MUST

- Never log `security_token`.

## Cross-references

`TransportOptions`, `CloudIdentity`, `apis/do_transaction`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
