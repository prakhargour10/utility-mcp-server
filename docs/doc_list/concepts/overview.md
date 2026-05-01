# Concept: overview

> **AI INSTRUCTIONS:** Read this first when the user asks "what does the SDK do" or before generating any integration plan.

## What the SDK is

The Pine Billing SDK is a single Rust core (`pine-billing-core`) projected via UniFFI into Kotlin (Android + JVM), with Swift / Python / Node.js / C planned (roadmap). It is a **payment transaction client** that talks to Pinelabs PoS terminals over one of several transports.

## What the SDK is NOT

- It is **not** a payment gateway. It does not hold funds.
- It does **not** persist any durable state to disk. Reconciliation is merchant-driven via `event_id` + `check_status`.
- It does **not** phone home. There is zero telemetry.
- It does **not** handle card data, PIN, or CVV. Those never enter the SDK process.

## Shape of an integration

1. Construct one `PineBillingSdk` per process (`constructor`).
2. Optionally `set_transport(...)` if the choice is dynamic.
3. For each merchant transaction, call `do_transaction(request, listener)`.
4. On `on_started(event_id)`, persist the `event_id` against the merchant order id.
5. On `on_success` or `on_failure`, finalise the merchant order.
6. After process restart, reconcile any open order via `check_status(event_id)`.

## Architecture (informational)

- `pine-billing-core` — pure domain logic. No I/O.
- `pine-billing-adapters` — concrete transport implementations.
- `pine-billing-ffi` — composition root + UniFFI bindings.

## Next docs

`lifecycle`, `transports`, `capabilities`, `error-handling`, `eventid-and-reconciliation`.
