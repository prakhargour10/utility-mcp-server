# Model: `CloudTransactionData` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Structured payload returned alongside `check_status` for the Cloud transport. Unknown tags fall through into `metadata`.

## Fields

| Name | Type | Required |
|---|---|---|
| `tid` | `string?` | - |
| `mid` | `string?` | - |
| `payment_mode` | `string?` | - |
| `amount` | `string?` | - |
| `batch_number` | `string?` | - |
| `rrn` | `string?` | - |
| `approval_code` | `string?` | - |
| `invoice_number` | `string?` | - |
| `customer_vpa` | `string?` | - |
| `acquirer_id` | `string?` | - |
| `acquirer_name` | `string?` | - |
| `transaction_date` | `string?` | - |
| `transaction_time` | `string?` | - |
| `amount_in_paisa` | `string?` | - |
| `original_amount` | `string?` | - |
| `final_amount` | `string?` | - |
| `transaction_log_id` | `string?` | - |
| `currency_minor_unit` | `string?` | - |
| `metadata` | `record<string,string>` | yes (may be empty) |

## Cross-references

`OperationStatus`, `apis/check_status`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
