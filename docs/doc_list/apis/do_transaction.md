# API: `do_transaction`

> **AI INSTRUCTIONS:** This file describes the public method `do_transaction` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
do_transaction(TransactionRequest request, TransactionListener listener)
```

## Purpose

Start a transaction. Returns immediately on success; the terminal-state result is delivered via `listener`.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `request` | `TransactionRequest` | yes | Validated synchronously before any I/O. |
| `listener` | `TransactionListener` | yes | `on_started` fires once with the SDK-allocated `event_id`, then exactly one of `on_success` / `on_failure`. |

## Returns

`void` (result delivered asynchronously through listener).

## Delivery model

Asynchronous. Callbacks fire on an SDK-internal worker thread. Generated UI code MUST marshal to the platform UI thread before touching widgets.

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — amount out of range, `billing_ref_no` blank, `currency` not 3 uppercase ASCII, `original_event_id` presence mismatch with `transaction_type`, `transport_options` variant ≠ active transport, Cloud `transport_options` missing, etc.
- **`SdkError.OperationInProgress`** — Another op is in flight on this SDK instance. Variant carries the active `event_id`.
- **`SdkError.NotConnected`** — Active transport requires a prior `connect()` and there is no link.
- **`SdkError.TransportUnavailable`** — Active transport cannot be reached (e.g. upstream PoS service not installed).
- **`SdkError.NotSupported`** — Active transport does not support this `transaction_type`.

## Errors delivered via `listener.onFailure`

Any error after `on_started` fires:

- `SdkError.TransactionFailed { detail, terminal_response_code }` — terminal returned non-success.
- `SdkError.Timeout` — no reply within budget. On Cloud, follow up with `check_status`.
- `SdkError.TransportError` — mid-stream link failure.
- `SdkError.Cancelled` — caller-initiated cancel succeeded mid-flight (Cloud).
- `SdkError.Network` / `ConnectionTimeout` / `ReadTimeout` / `NonSuccessHttp` — Cloud HTTP-layer failures observed after upload started.
- `SdkError.Internal` — SDK defect.

## Listener threading & re-entry contract

- `on_started`, `on_success`, `on_failure` all fire on the SDK worker thread. They are serialised — never overlap.
- Calling `sdk.doTransaction(...)` from inside `onSuccess`/`onFailure` is **unsafe** (same worker, deadlock risk). Marshal to a fresh executor first.
- Inside `onStarted`: synchronous Room DAOs and durable persistence are SAFE; LiveData/Flow main-thread observers and UI mutations are NOT — marshal to main thread first.
- See `concepts/threading.md` for the full contract.

## MUST

- Disable the trigger control on `listener.onStarted` and re-enable on terminal-state callback.
- When `TARGET_TRANSPORT == Cloud`, populate `request.transportOptions` with the Cloud variant (transaction_number, sequence_number, allowed_payment_mode, total_invoice_amount, txn_type, auto_cancel_duration_minutes are mandatory).
- When `transaction_type ∈ {Refund, Void, Capture}`, set `originalEventId` to the previous Sale's `event_id`.
- Treat `TransactionStatus.Pending` (Cloud only) as a not-yet-settled state — drive subsequent state via `check_status`.
- On Android: dispatch off the main thread. The façade throws `IllegalStateException` otherwise.

## MUST NOT

- Do not block in any callback.
- Do not call `do_transaction` again before receiving the terminal-state callback for the previous one.
- Do not call `sdk.doTransaction(...)` from inside the listener without marshalling to a fresh executor.
- Do not log card data, PIN, full PAN, or tokens. `masked_pan` only at debug level.
- Do not pass a hand-built UUID — `event_id` is allocated by the SDK.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✓ |
| Tcp | ✗ `NotSupported` (v1 placeholder) |
| Cloud | ✓ ✚ resolves with `Pending` |
| PadController | ✓ |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
val request = TransactionRequest(
    amount = 19_900uL,           // 19_900 paise = INR 199.00
    currency = "INR",
    billingRefNo = "INV-2025-001",
    invoiceNo = "INV-2025-001",
    transactionType = TransactionType.SALE,
    originalEventId = null,
    referenceId = "order-abc",
    metadata = null,
    merchantId = null,           // AppToApp derives identity from terminal
    terminalId = null,
    allowedPaymentModes = null,
    transportOptions = null,
)
sdk.doTransaction(request, object : TransactionListener {
    override fun onStarted(eventId: String) { /* persist eventId BEFORE returning */ }
    override fun onSuccess(result: TransactionResult) { /* finalise order */ }
    override fun onFailure(error: SdkException) { /* dispatch by variant */ }
})
```

### Android (Java) — shipping

> Java samples reference `Unsigned.toUInt(...)` / `Unsigned.toULong(...)` from `com.merchant.pos`. See `languages/jvm/setup.md` § 5 for the canonical helper.

```java
TransactionRequest request = new TransactionRequest(
    Unsigned.toULong(19_900L), "INR", "INV-2025-001", "INV-2025-001",
    TransactionType.SALE, null, "order-abc", null, null, null, null, null
);
sdk.doTransaction(request, new TransactionListener() {
    @Override public void onStarted(String eventId) { /* persist */ }
    @Override public void onSuccess(TransactionResult result) { /* finalise */ }
    @Override public void onFailure(SdkException error) { /* dispatch */ }
});
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade. There is no Android `Context` and no main-thread guard.

```kotlin
val request = TransactionRequest(
    amount = 19_900uL,           // 19_900 paise = INR 199.00
    currency = "INR",
    billingRefNo = "INV-2025-001",
    invoiceNo = "INV-2025-001",
    transactionType = TransactionType.SALE,
    originalEventId = null,
    referenceId = "order-abc",
    metadata = null,
    merchantId = null,           // AppToApp derives identity from terminal
    terminalId = null,
    allowedPaymentModes = null,
    transportOptions = null,
)
sdk.doTransaction(request, object : TransactionListener {
    override fun onStarted(eventId: String) { /* persist eventId BEFORE returning */ }
    override fun onSuccess(result: TransactionResult) { /* finalise order */ }
    override fun onFailure(error: SdkException) { /* dispatch by variant */ }
})
```

### JVM (Java) — shipping

> Java samples reference `Unsigned.toUInt(...)` / `Unsigned.toULong(...)` from `com.merchant.pos`. See `languages/jvm/setup.md` § 5 for the canonical helper.

```java
TransactionRequest request = new TransactionRequest(
    Unsigned.toULong(19_900L), "INR", "INV-2025-001", "INV-2025-001",
    TransactionType.SALE, null, "order-abc", null, null, null, null, null
);
sdk.doTransaction(request, new TransactionListener() {
    @Override public void onStarted(String eventId) { /* persist */ }
    @Override public void onSuccess(TransactionResult result) { /* finalise */ }
    @Override public void onFailure(SdkException error) { /* dispatch */ }
});
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.doTransaction(request: request, listener: MyListener())
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.do_transaction(request, MyListener())
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.doTransaction(request, listener);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_do_transaction(sdk, &request, &listener, &err);
```

## Next docs to fetch

- Models: `TransactionRequest`, `TransactionResult`, `TransactionListener`, `TransportOptions`, `AppToAppTransactionOptions`, `CloudTransactionOptions`, `PadControllerTransactionOptions`, `SdkError`
- Concepts: `lifecycle`, `eventid-and-reconciliation`, `error-handling`, `result-payload`, `threading`, `transports`
- Languages: `languages/android/integration`, `languages/jvm/integration`, `languages/jvm/setup` § 5 (Unsigned helper)

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
