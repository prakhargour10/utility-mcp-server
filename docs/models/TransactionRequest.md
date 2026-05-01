# Model: `TransactionRequest` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Inputs for a single transaction. Validated synchronously in core before any I/O.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `amount` | `u64` | yes | Lowest currency unit (paise). 0 < amount ≤ 99_999_999. |
| `currency` | `string?` | no | ISO-4217. 3 ASCII uppercase letters. Default INR. |
| `billing_ref_no` | `string` | yes | Non-blank after trim. |
| `invoice_no` | `string?` | no | No SDK shape validation; accepted verbatim by terminal/back-end. |
| `transaction_type` | `TransactionType` | yes | See TransactionType. |
| `original_event_id` | `string?` | conditional | Required iff transaction_type ∈ {Refund, Void, Capture}; rejected otherwise. |
| `reference_id` | `string?` | no | Free-form merchant reference echoed on TransactionResult. Max 64 chars. |
| `metadata` | `record<string,string>?` | no | Max 10 entries; each value ≤ 256 chars. Never logged. |
| `merchant_id` | `string?` | conditional | Required for non-AppToApp transports (TCP, Cloud). |
| `terminal_id` | `string?` | conditional | Required for non-AppToApp transports (TCP, Cloud). |
| `allowed_payment_modes` | `sequence<PaymentMode>?` | no | Filter for terminal payment selection. IGNORED on Cloud — use CloudTransactionOptions.allowed_payment_mode. |
| `transport_options` | `TransportOptions?` | conditional | Variant MUST match active transport. REQUIRED on Cloud. |

## MUST

- Enforce all bounds client-side before calling do_transaction.
- Pick the right TransportOptions variant for the active transport.

## MUST NOT

- Do not pass amount as float or string; it is u64 paise.
- Do not log metadata.
- Do not pass card data, PII or PCI fields here.

## Cross-references

`TransactionType`, `TransportOptions`, `PaymentMode`, `TransactionResult`, `TransactionListener`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
