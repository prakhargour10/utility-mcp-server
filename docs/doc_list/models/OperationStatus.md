# Model: `OperationStatus` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Result of `check_status`. Field presence depends on `state`.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `state` | `OperationState` | yes | |
| `result` | `TransactionResult?` | conditional | Set iff `state == Completed`. |
| `failure_detail` | `string?` | conditional | Set iff `state == Failed`. |
| `terminal_response_code` | `string?` | conditional | May be set iff `state == Failed`. |
| `cloud_transaction_data` | `CloudTransactionData?` | conditional | Cloud-only. Always null for non-Cloud transports. |

## Cross-references

`OperationState`, `TransactionResult`, `CloudTransactionData`, `apis/check_status`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
