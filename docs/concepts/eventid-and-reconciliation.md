# Concept: eventid-and-reconciliation

> **AI INSTRUCTIONS:** Use this file to design the merchant-side persistence model.

## What event_id is

- A UUIDv4 allocated by the SDK at the moment `do_transaction` / `test_print` is accepted.
- Delivered to the merchant via `on_started(event_id)`.
- Echoed in every subsequent callback and in `TransactionResult.event_id`.
- The single key used by `cancel(event_id, ...)` and `check_status(event_id, ...)`.

## Cloud caveat

For Cloud, `cancel` / `check_status` use the upstream `PlutusTransactionReferenceID` (mirrored into `TransactionResult.transaction_id` on the `Pending` callback) — NOT the SDK event_id. The SDK does not maintain an event_id ↔ cloud-ref mapping; the merchant passes the cloud ref directly.

## Reconciliation pattern (mandatory in generated code)

```
1. orderId = createMerchantOrder(...)
2. listener.onStarted(eventId):
       persist(orderId, eventId, status=PENDING)
3. listener.onSuccess(result):
       update(orderId, eventId, status=SUCCESS, result)
4. listener.onFailure(error):
       update(orderId, eventId, status=FAILED, error)
5. on process restart, for every orderId where status=PENDING:
       OperationStatus s = sdk.checkStatus(eventId, options)
       map(s.state) → final order status
```

For Cloud, persist `transaction_id` (PlutusTransactionReferenceID) once you receive `status = Pending` and use that for subsequent `cancel` / `check_status` calls.

## OperationState semantics for reconciliation

| state | Action |
|---|---|
| `Pending` / `InFlight` | Wait, retry `check_status` after a backoff. |
| `Completed` | Use `result` and `cloud_transaction_data`. Mark order success. |
| `Failed` | Use `failure_detail` + `terminal_response_code`. |
| `Cancelled` | Mark order cancelled. |
| `Unknown` | SDK has no record. Reconcile via merchant + (Cloud) upstream records. Treat as authoritative-pending until upstream confirms. |

## MUST

- Persist `event_id` (and Cloud `transaction_id`) durably before `on_started` returns.
- Implement `Unknown` recovery — it WILL happen after process restart.

## MUST NOT

- Do not generate UUIDs on the merchant side and pass them as `event_id` — the SDK rejects unknown ids on AppToApp/PadController.
- Do not use `billing_ref_no` as a primary reconciliation key — it is echo-only and not unique by SDK design.

## Next docs

`lifecycle`, `result-payload`.
