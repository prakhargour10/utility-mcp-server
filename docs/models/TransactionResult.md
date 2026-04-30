# Model: `TransactionResult` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Terminal-state outcome of a single transaction. Curated subset of the underlying terminal response; null fields = terminal did not provide.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `event_id` | `string` | yes | SDK-allocated UUIDv4 — same value delivered on on_started. |
| `status` | `TransactionStatus` | yes | Success | Failed | Pending. |
| `billing_ref_no` | `string?` | - | Echo of TransactionRequest.billing_ref_no. |
| `reference_id` | `string?` | - | Echo of request.reference_id. |
| `transaction_id` | `string?` | - | Cloud: PlutusTransactionReferenceID. |
| `rrn` | `string?` | - | Retrieval Reference Number. |
| `auth_code` | `string?` | - | Acquirer auth code. |
| `amount` | `string?` | - | Echo, terminal-formatted. |
| `masked_pan` | `string?` | - | Last4 / masked. Log only at debug. |
| `card_holder_name` | `string?` | - |  |
| `card_type` | `string?` | - |  |
| `acquirer` | `string?` | - |  |
| `merchant_id` | `string?` | - |  |
| `terminal_id` | `string?` | - |  |
| `invoice_no` | `string?` | - |  |
| `batch_no` | `string?` | - |  |
| `date` | `string?` | - |  |
| `time` | `string?` | - |  |
| `charge_slip_print_data` | `string?` | - |  |
| `response_code` | `string?` | - |  |
| `response_message` | `string?` | - |  |
| `metadata` | `record<string,string>?` | - | Transport-specific extras (NCMC keys, cloud.transactionData.*). |

## MUST

- Match results to requests via event_id or billing_ref_no.

## MUST NOT

- Do not log full PAN. masked_pan only at debug.

## Cross-references

`TransactionStatus`, `TransactionRequest`, `TransactionListener`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
