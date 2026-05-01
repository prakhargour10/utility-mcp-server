# Concept: lifecycle

> **AI INSTRUCTIONS:** Use this file to enforce correct lifecycle handling in generated code (state transitions, callback ordering, threading).

## SDK instance lifecycle

```
constructor → [active] → (disconnect)? → drop
```

- One instance per process.
- `set_transport` swaps the active transport in place. Implicit `disconnect()` of the previous transport.
- Drop / dispose closes any open transport link (Android façade implements `AutoCloseable`).

## Transaction lifecycle

```
do_transaction(...)
   │
   ├── synchronous validation (InvalidInput / OperationInProgress / NotConnected / NotSupported / TransportUnavailable)
   │       └── if it throws here → NO callbacks fire
   │
   └── accepted
       │
       ├── on_started(event_id)        ← exactly once, on SDK worker thread
       │
       └── exactly one of:             ← on the same SDK worker thread, serialised
           ├── on_success(TransactionResult)
           └── on_failure(SdkError)
```

For Cloud, `on_success` may carry `status = Pending`. The merchant
then drives subsequent state via `check_status` until
`state ∈ {Completed, Failed, Cancelled}`.

## Callback threading contract

- Callbacks fire on an SDK-internal worker thread.
- Callbacks for the same listener are serialised — never overlap.
- Callbacks NEVER fire on the caller's stack frame.
- Generated code MUST marshal to the platform UI thread before touching widgets.
- Generated code MUST NOT block in any callback.

## Concurrency

- Only one listener-style operation per SDK instance at a time.
- A second `do_transaction` / `test_print` / `discover_terminals` while one is in flight raises `OperationInProgress(active_event_id)` synchronously.
- `cancel` and `check_status` run on the caller thread and are NOT gated by the in-flight op — they are the recovery surface.

## Crash recovery

- On process restart, `check_status(event_id)` may return `state = Unknown` for events allocated by a prior process. That is a valid recovery answer; reconcile via merchant records and (Cloud) the upstream.

## Next docs

`threading`, `eventid-and-reconciliation`, `error-handling`.
