# Model: `TransactionResult` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Terminal-state outcome of a single transaction. Curated subset of the underlying terminal response; null fields = terminal did not provide.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `event_id` | `string` | yes | SDK-allocated UUIDv4 — same value delivered on `on_started`. |
| `status` | `TransactionStatus` | yes | Success / Failed / Pending. |
| `billing_ref_no` | `string?` | - | Echo of `TransactionRequest.billing_ref_no`. |
| `reference_id` | `string?` | - | Echo of `request.reference_id`. |
| `transaction_id` | `string?` | - | Cloud: `PlutusTransactionReferenceID`. |
| `rrn` | `string?` | - | Retrieval Reference Number. |
| `auth_code` | `string?` | - | Acquirer auth code. |
| `amount` | `string?` | - | **Display-only** — terminal-formatted. See "amount semantics" below. |
| `masked_pan` | `string?` | - | Last4 / masked. Log only at debug. |
| `card_holder_name` | `string?` | - | |
| `card_type` | `string?` | - | |
| `acquirer` | `string?` | - | |
| `merchant_id` | `string?` | - | |
| `terminal_id` | `string?` | - | |
| `invoice_no` | `string?` | - | |
| `batch_no` | `string?` | - | |
| `date` | `string?` | - | |
| `time` | `string?` | - | |
| `charge_slip_print_data` | `string?` | - | |
| `response_code` | `string?` | - | |
| `response_message` | `string?` | - | |
| `metadata` | `record<string,string>?` | - | Transport-specific extras (NCMC keys, `cloud.transactionData.*`). |

## `amount` semantics (MEDIUM-priority callout)

`TransactionResult.amount` is **terminal-formatted display** — never use it for reconciliation arithmetic. Always treat `request.amount` (paise) as authoritative.

| Transport | Format | Example |
|---|---|---|
| AppToApp | Echo of upstream `Detail.amount`. Typically major units (e.g. `"199.00"`), no currency symbol. | `"199.00"` |
| Cloud | Stringified value from upstream. **TODO:** unit (paise vs major) is endpoint-dependent — verify against your tenant. | `"19900"` or `"199.00"` |
| PADController | Terminal-formatted, varies by terminal model. | `"199.00"` |

## Expected populated fields per transport

| Field | AppToApp | Cloud | PADController |
|---|---|---|---|
| `event_id` | ✓ | ✓ | ✓ |
| `status` | ✓ | ✓ | ✓ |
| `billing_ref_no` | ✓ (echo) | ✓ (echo) | ✓ (echo) |
| `reference_id` | conditional (echo) | conditional (echo) | conditional (echo) |
| `transaction_id` | conditional | ✓ (`PlutusTransactionReferenceID` on Pending) | conditional |
| `rrn` | ✓ on Sale Success | ✗ on Pending; via `check_status` later | conditional |
| `auth_code` | ✓ on Sale Success | ✗ on Pending; via `check_status` later | conditional |
| `amount` | ✓ (display) | conditional | ✓ (display) |
| `masked_pan` | ✓ on Card | ✗ on Pending; via `check_status` later | conditional |
| `card_holder_name` | conditional | conditional | conditional |
| `card_type` | conditional | conditional | conditional |
| `acquirer` | conditional | conditional | conditional |
| `merchant_id` | ✗ (terminal-derived) | conditional | conditional |
| `terminal_id` | conditional | conditional | conditional |
| `invoice_no` | conditional (echo) | conditional (echo) | conditional (echo) |
| `batch_no` | conditional | conditional | conditional |
| `date` / `time` | conditional | conditional | conditional |
| `charge_slip_print_data` | ✓ when receipt printing | conditional | conditional |
| `response_code` | ✓ | ✓ | ✓ |
| `response_message` | ✓ | ✓ | ✓ |
| `metadata` | NCMC keys when present | `cloud.transactionData.*` after settlement | extras pass-through |

> **TODO:** the per-transport population table above is best-effort, derived from the UDL and adapter source. Confirm exact field population on a real Pinelabs terminal before relying on "✓"-marked fields in production.

## MUST

- Always check `status` before accessing transactional fields.
- Match results to requests via `event_id` (or `billing_ref_no`).

## MUST NOT

- Do not log full PAN. `masked_pan` only at debug.
- Do not parse `amount` as a paise integer — it is display-only.

## Cross-references

`TransactionStatus`, `TransactionRequest`, `TransactionListener`, `concepts/result-payload`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
