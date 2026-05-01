# Concept: result-payload

> **AI INSTRUCTIONS:** Use this file when emitting code that consumes `TransactionResult` or `OperationStatus`.

## TransactionResult — what is guaranteed

- `event_id` — always set; matches `on_started`.
- `status` — always set.
- All other fields are `string?` (or omitted on certain transports).
  Generated code MUST handle null for every optional field.

## status semantics

| status | Field set guarantee |
|---|---|
| `Success` | At least `event_id`, `status`, `billing_ref_no` (echoed). Most other fields populated when terminal provides them. |
| `Failed` | `response_code` / `response_message` typically set. Other transactional fields may be null. |
| `Pending` (Cloud only) | `event_id`, `status`, `transaction_id` (= PlutusTransactionReferenceID). All other fields null. Drive next state via `check_status`. |

## OperationStatus — field-presence rules

- `state == Completed` → `result` is set; others null (except `cloud_transaction_data` on Cloud).
- `state == Failed` → `failure_detail` is set; `terminal_response_code` may be set; `result` is null.
- `state ∈ {Cancelled, Pending, InFlight, Unknown}` → all other fields null.

## TransactionResult.amount semantics

`amount` is **terminal-formatted display** — it is NOT a paise amount
the merchant can use for reconciliation arithmetic. The format varies
per transport:

| Transport | `amount` shape | Example | Use for arithmetic? |
|---|---|---|---|
| AppToApp | Terminal-formatted string echoed from upstream `Detail.amount`. Typically major units like `"199.00"` (no currency symbol). | `"199.00"` | ✗ display-only |
| Cloud | Stringified value from upstream response. Unit not contractually fixed across endpoints — verify against your tenant. **TODO:** confirm exact unit (paise vs major) per Cloud endpoint. | `"19900"` (paise) or `"199.00"` (major) — tenant-dependent | ✗ display-only |
| PADController | Terminal-formatted, varies by terminal model and transaction type. | `"199.00"` | ✗ display-only |

> **Reconciliation rule:** Always use `request.amount` (paise, `u64`)
> as the authoritative amount in your books. Treat
> `result.amount` as display-only.

## metadata pass-through (TransactionResult.metadata)

Stable keys; new keys may be added in minor releases, existing keys
never removed without a major bump.

- AppToApp NCMC: `ncmc.serviceID`, `ncmc.serviceMI`,
  `ncmc.isTransitMode`, `ncmc.paymentMode`, `ncmc.serviceData`,
  `ncmc.AppId`.
- Cloud raw `TransactionData`: flattened under
  `cloud.transactionData.*`. Null on `Pending`.

## MUST

- Always check `status` before accessing transactional fields.
- Echo `event_id` and `billing_ref_no` (or `reference_id`) in
  merchant logs to correlate with the request.
- Use `request.amount` (paise) for ledger / reconciliation; use
  `result.amount` only for display.

## MUST NOT

- Do not assume `auth_code` / `rrn` / `transaction_id` are non-null
  on `Failed`.
- Do not log `masked_pan` above debug level.
- Do not parse `result.amount` as a paise integer — it may be major
  units with a decimal point.

## Next docs

`lifecycle`, `eventid-and-reconciliation`, `models/TransactionResult`.
