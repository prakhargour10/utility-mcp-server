# API: `do_transaction`

> **AI INSTRUCTIONS:** This file describes the public method `do_transaction` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
do_transaction(TransactionRequest request, TransactionListener listener)
```

## Purpose

Start a transaction. Returns immediately on success; the terminal-state result is delivered via listener.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `request` | `TransactionRequest` | yes | Validated synchronously before any I/O. See validation rules below. |
| `listener` | `TransactionListener` | yes | on_started fires once with the SDK-allocated event_id, then exactly one of on_success / on_failure. |


## Returns

void (result delivered asynchronously through listener).

## Delivery model

Asynchronous. Callbacks fire on an SDK-internal worker thread. Generated UI code MUST marshal to the platform UI thread before touching widgets.

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — amount out of range, billing_ref_no blank, currency not 3 uppercase ASCII, original_event_id presence mismatch with transaction_type, transport_options variant ≠ active transport, Cloud transport_options missing, etc.
- **`SdkError.OperationInProgress`** — Another op is in flight on this SDK instance. Variant carries the active event_id.
- **`SdkError.NotConnected`** — Active transport requires a prior connect() and there is no link.
- **`SdkError.TransportUnavailable`** — Active transport cannot be reached (e.g. MasterApp service not installed).
- **`SdkError.NotSupported`** — Active transport does not support this transaction_type.

## MUST

- Disable the trigger control on listener.on_started and re-enable on terminal-state callback.
- When TARGET_TRANSPORT == Cloud, populate request.transport_options with the Cloud variant (transaction_number, sequence_number, allowed_payment_mode, total_invoice_amount, txn_type, auto_cancel_duration_minutes are mandatory).
- When transaction_type ∈ {Refund, Void, Capture}, set original_event_id to the previous Sale's event_id.
- Treat TransactionStatus.Pending (Cloud only) as a not-yet-settled state — drive subsequent state via check_status.

## MUST NOT

- Do not block in any callback.
- Do not call do_transaction again before receiving the terminal-state callback for the previous one.
- Do not log card data, PIN, full PAN, or tokens. masked_pan only at debug level.
- Do not pass a hand-built UUID — event_id is allocated by the SDK.

## Per-language call shape

```kotlin
// Kotlin
val sdk = PineBillingSdk(config, /*appToAppBridge*/null, /*platformBridge*/null)
```
```swift
// Swift
let sdk = try PineBillingSdk(config: config, appToAppBridge: nil, platformBridge: nil)
```
```python
# Python
sdk = PineBillingSdk(config=config, app_to_app_bridge=None, platform_bridge=None)
```
```javascript
// Node.js
const sdk = new PineBillingSdk(config, /*appToAppBridge*/null, /*platformBridge*/null);
```
```c
/* C */
PineBillingSdk* sdk = pine_billing_sdk_new(&config, NULL, NULL, &err);
```
> The above is the constructor shape; for non-constructor APIs use
> `sdk.do_transaction(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `TransactionRequest`, `TransactionResult`, `TransactionListener`, `TransportOptions`, `AppToAppTransactionOptions`, `CloudTransactionOptions`, `PadControllerTransactionOptions`, `SdkError`
- Concepts: `lifecycle`, `eventid-and-reconciliation`, `error-handling`, `result-payload`, `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
