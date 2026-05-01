# API: `cancel`

> **AI INSTRUCTIONS:** This file describes the public method `cancel` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
cancel(string event_id, CancelOptions? options)
```

## Purpose

Best-effort cancel of an in-flight op identified by `event_id`. If the terminal already committed, the op is NOT cancelled and eventual outcome is `Success`.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `event_id` | `string` | yes | AppToApp / TCP / PADController: the SDK-allocated UUID from `on_started`. **Cloud:** the `PlutusTransactionReferenceID` echoed in `TransactionResult.transaction_id`. |
| `options` | `CancelOptions?` | conditional | Required for Cloud (`CancelOptions.Cloud{merchant_id, security_token, identity, amount}`); MUST be null for other transports. |

## Returns

`void` on accepted-by-transport. Synchronous; on Cloud bounded by `cloud.connect_timeout_ms` + `cloud.read_timeout_ms`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Cloud transport without options, non-Cloud transport with options, malformed amount.
- **`SdkError.NotSupported`** — Active transport has no cancel mechanism (today: AppToApp, PADController).
- **`SdkError.TransportError` / `Timeout` / `Network` / `ConnectionTimeout` / `ReadTimeout` / `NonSuccessHttp`** — Cloud HTTP-layer failures.

## Interaction with in-flight `do_transaction`

On Cloud, a successful `cancel` mid-flight causes the in-flight `do_transaction` listener to fire `onFailure(SdkError.Cancelled)` once the SDK observes the cancellation.

## MUST

- Use the exact `event_id` from `on_started` (or the `PlutusTransactionReferenceID` for Cloud).
- Wrap the call in the platform-idiomatic async primitive (it blocks).

## MUST NOT

- Do not assume "cancel succeeded" means the transaction did not happen — re-check via `check_status` (Cloud only).
- Do not pass `CancelOptions::Cloud` on a non-Cloud transport.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✗ `NotSupported` |
| Tcp | ✗ `NotSupported` |
| Cloud | ✓ — `CancelOptions::Cloud` REQUIRED |
| PadController | ✗ `NotSupported` (v1) |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
sdk.cancel(eventId, /*options*/ null)                                  // AppToApp/PADController v1: NotSupported
// Cloud:
val opts = CancelOptions.Cloud(CloudCancelOptions(
    merchantId = "MID", securityToken = TOKEN,
    identity = CloudIdentity.Imei("STORE-POS", "IMEI"), amount = "19900"
))
sdk.cancel(plutusTxnRefId, opts)
```

### Android (Java) — shipping

> Java samples reference `Unsigned.toUInt(...)` / `Unsigned.toULong(...)` from `com.merchant.pos`. See `languages/jvm/setup.md` § 5 for the canonical helper.

```java
sdk.cancel(eventId, null);
CancelOptions opts = new CancelOptions.Cloud(new CloudCancelOptions(
    "MID", TOKEN, new CloudIdentity.Imei("STORE-POS", "IMEI"), "19900"));
sdk.cancel(plutusTxnRefId, opts);
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade. There is no main-thread guard.

```kotlin
sdk.cancel(eventId, /*options*/ null)                                  // AppToApp/PADController v1: NotSupported
// Cloud:
val opts = CancelOptions.Cloud(CloudCancelOptions(
    merchantId = "MID", securityToken = TOKEN,
    identity = CloudIdentity.Imei("STORE-POS", "IMEI"), amount = "19900"
))
sdk.cancel(plutusTxnRefId, opts)
```

### JVM (Java) — shipping

> Java samples reference `Unsigned.toUInt(...)` / `Unsigned.toULong(...)` from `com.merchant.pos`. See `languages/jvm/setup.md` § 5 for the canonical helper.

```java
sdk.cancel(eventId, null);
CancelOptions opts = new CancelOptions.Cloud(new CloudCancelOptions(
    "MID", TOKEN, new CloudIdentity.Imei("STORE-POS", "IMEI"), "19900"));
sdk.cancel(plutusTxnRefId, opts);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.cancel(eventId: id, options: .cloud(opts))
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.cancel(event_id=event_id, options=opts_or_none)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.cancel(eventId, options);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_cancel(sdk, event_id, options_or_null, &err);
```

## Next docs to fetch

- Models: `CancelOptions`, `CloudCancelOptions`, `CloudIdentity`, `SdkError`
- Concepts: `eventid-and-reconciliation`, `lifecycle`, `error-handling`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
