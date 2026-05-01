# API: `check_status`

> **AI INSTRUCTIONS:** This file describes the public method `check_status` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
check_status(string event_id, CheckStatusOptions? options) -> OperationStatus
```

## Purpose

Query the lifecycle state of a prior op by event_id. Used for crash-recovery and reconciliation.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `event_id` | `string` | yes | Same semantics as cancel. |
| `options` | `CheckStatusOptions?` | conditional | Required for Cloud (CheckStatusOptions.Cloud{merchant_id,security_token,identity}); MUST be null for other transports. |


## Returns

OperationStatus. state == Unknown when SDK has no record of the id (this is a valid recovery answer, not an error).

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Cloud transport without options, non-Cloud transport with options.
- **`SdkError.NotSupported`** — Active transport (today: AppToApp).
- **`SdkError.Network / Timeout / ConnectionTimeout / ReadTimeout / NonSuccessHttp`** — Cloud HTTP-layer failures.

## MUST

- Treat OperationState.Unknown as 'not in this SDK instance' — proceed to reconcile via merchant records.
- On Cloud, inspect OperationStatus.cloud_transaction_data when state == Completed.

## MUST NOT

- Do not poll in tight loops; respect cloud.read_timeout_ms.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✗ `NotSupported` |
| Tcp | ✗ `NotSupported` |
| Cloud | ✓ — `CheckStatusOptions::Cloud` REQUIRED |
| PadController | ✗ `NotSupported` (v1) |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
val status = sdk.checkStatus(eventId, /*options*/ null)               // AppToApp/PAD v1: NotSupported
// Cloud:
val opts = CheckStatusOptions.Cloud(CloudCheckStatusOptions(
    merchantId = "MID", securityToken = TOKEN,
    identity = CloudIdentity.Imei("STORE-POS", "IMEI")
))
val status = sdk.checkStatus(plutusTxnRefId, opts)
```

### Android (Java) — shipping

```java
OperationStatus status = sdk.checkStatus(eventId, null);
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
val status = sdk.checkStatus(eventId, /*options*/ null)               // AppToApp/PAD v1: NotSupported
// Cloud:
val opts = CheckStatusOptions.Cloud(CloudCheckStatusOptions(
    merchantId = "MID", securityToken = TOKEN,
    identity = CloudIdentity.Imei("STORE-POS", "IMEI")
))
val status = sdk.checkStatus(plutusTxnRefId, opts)
```

### JVM (Java) — shipping

```java
OperationStatus status = sdk.checkStatus(eventId, null);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
let status = try sdk.checkStatus(eventId: id, options: opts)
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
status = sdk.check_status(event_id=event_id, options=opts_or_none)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
const status = sdk.checkStatus(eventId, options);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_check_status(sdk, event_id, options, &out_status, &err);
```

## Next docs to fetch

- Models: `CheckStatusOptions`, `CloudCheckStatusOptions`, `OperationStatus`, `OperationState`, `CloudTransactionData`, `SdkError`
- Concepts: `eventid-and-reconciliation`, `result-payload`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
