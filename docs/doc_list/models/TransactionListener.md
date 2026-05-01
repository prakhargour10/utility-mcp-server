# Model: `TransactionListener` (callback interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Callback for `do_transaction`. Exactly one of `on_success` / `on_failure` fires per call, after exactly one `on_started`.

## Methods

| Name | Signature | Notes |
|---|---|---|
| `on_started` | `on_started(string event_id)` | Fires once with the SDK-allocated UUIDv4. |
| `on_success` | `on_success(TransactionResult result)` | Terminal-state success. |
| `on_failure` | `on_failure(SdkError error)` | Terminal-state failure. |

### Per-language signature projection

| Binding | Method form |
|---|---|
| Kotlin | `override fun onStarted(eventId: String)`, `override fun onSuccess(result: TransactionResult)`, `override fun onFailure(error: SdkException)` |
| Java   | `@Override public void onStarted(String eventId)`, `@Override public void onSuccess(TransactionResult result)`, `@Override public void onFailure(SdkException error)` |
| Swift  | `func onStarted(eventId: String)`, `func onSuccess(result: TransactionResult)`, `func onFailure(error: SdkError)` (roadmap) |
| Python | `def on_started(self, event_id): ...`, `def on_success(self, result): ...`, `def on_failure(self, error): ...` (roadmap) |
| Node.js| `onStarted(eventId)`, `onSuccess(result)`, `onFailure(error)` (roadmap) |
| C      | function-pointer table (roadmap) |

## Threading & ordering contract

- All callbacks fire from the **SDK-internal worker thread** — never on the calling thread.
- Callbacks for the same listener are **serialised**; `on_started` and `on_success` / `on_failure` never overlap, but they DO share the same worker thread.
- `on_started` fires before either terminal-state callback iff the SDK accepted the call.
- If `do_transaction` raised an `SdkError` synchronously, NO callback fires.
- Callbacks MUST NOT block — would stall the SDK worker.
- Callbacks MUST NOT touch UI directly — marshal back to platform UI thread first.
- Calling `sdk.doTransaction(...)` (or any blocking SDK method) **inside** `on_success` / `on_failure` is **unsafe** — same worker thread, deadlock risk. Always marshal to a fresh executor first.

## Cancellation interaction

On Cloud, a successful `cancel(event_id, …)` mid-flight causes the in-flight `do_transaction` listener to fire `on_failure(SdkError.Cancelled)` once the SDK observes the cancellation. AppToApp / PADController v1 raise `NotSupported` from `cancel` and never affect an in-flight op.

## MUST

- Persist `event_id` durably **before** `on_started` returns.
- Disable trigger control on `on_started`, re-enable on terminal-state callback.
- Marshal to platform UI thread before touching widgets in any callback.

## MUST NOT

- Do not block in any callback.
- Do not call any `PineBillingSdk` method from inside a callback without marshalling to a fresh executor first.

## Cross-references

`TransactionResult`, `SdkError`, `apis/do_transaction`, `concepts/threading`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
