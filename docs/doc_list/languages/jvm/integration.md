# JVM — Integration (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** No main-thread guard on JVM; no Android `Context`; no AppToApp. Cloud is the primary transport.

## Lifecycle

- Construct ONCE per process and reuse. The SDK is not built for per-call construction.
- `PineBillingSdk` is `AutoCloseable`; close on shutdown if you care about clean teardown.

## Threading

- Listener callbacks fire on an SDK-internal worker thread. Marshal to your platform's preferred executor before touching shared state under contention.
- Calling another SDK method from inside a listener callback is unsafe (same worker; deadlock risk). Use a fresh executor.

## Cloud usage

- Configure `cloud.base_url`, `cloud.type` (`SANDBOX` or `PROD`), and timeouts at construction.
- Pass `transport_options = TransportOptions.Cloud(...)` on every `do_transaction`.
- Use `transaction_id` (the `PlutusTransactionReferenceID`) — NOT the SDK `event_id` — when calling `cancel` / `check_status` on Cloud.

## Persistence

- Persist `event_id` AND Cloud `transaction_id` durably the moment `on_started` fires. Reconciliation depends on both.
