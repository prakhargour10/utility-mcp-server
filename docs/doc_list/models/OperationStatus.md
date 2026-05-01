# Model: `OperationStatus` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Result of check_status. Field presence depends on state.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `state` | `OperationState` | yes | Drives presence of other fields. |
| `result` | `TransactionResult?` | - | Set iff state == Completed. |
| `failure_detail` | `string?` | - | Set iff state == Failed. |
| `terminal_response_code` | `string?` | - | Optional alongside failure_detail. |
| `cloud_transaction_data` | `CloudTransactionData?` | - | Cloud-only. Populated by GetCloudBasedTxnStatus once settled. |

## MUST

- Switch on state before reading other fields.

## MUST NOT

- Do not assume result is non-null when state != Completed.

## Cross-references

`OperationState`, `TransactionResult`, `CloudTransactionData`, `check_status`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
