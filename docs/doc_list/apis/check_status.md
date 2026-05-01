# API: `check_status`

> **AI INSTRUCTIONS:** This file describes the public method `check_status` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
OperationStatus check_status(string event_id, CheckStatusOptions? options)
```

## Purpose

Query the lifecycle state of a prior op. Used for crash-recovery and reconciliation. Returns `OperationStatus` whose `state` is `Unknown` when the SDK has no record of the id (does NOT raise `InvalidInput` for unknown ids).

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `event_id` | `string` | yes | AppToApp / TCP / PADController: the SDK-allocated UUID. **Cloud:** the `PlutusTransactionReferenceID`. |
| `options` | `CheckStatusOptions?` | conditional | Required for Cloud; MUST be null for other transports. |

## Returns

`OperationStatus` — see model.

## Delivery model

Synchronous. AppToApp / PADController v1 raise `NotSupported` immediately. Cloud performs an HTTPS POST bounded by configured timeouts.

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Cloud transport without options, non-Cloud transport with options.
- **`SdkError.NotSupported`** — AppToApp / PADController v1 / Tcp.
- **`SdkError.TransportError` / `Timeout` / `Network` / `ConnectionTimeout` / `ReadTimeout` / `NonSuccessHttp`** — Cloud HTTP-layer failures.

## Cloud status code → `OperationState` map

| Upstream code | `OperationState` |
|---|---|
| `0` | `Completed` |
| `1`-family | `Failed` |
| `1001` (`TXN UPLOADED`) | `InFlight` |
| unknown | `InFlight` (raw response in `failure_detail` / `terminal_response_code`) |

The SDK never auto-fails on unknown codes.

## MUST

- Persist `event_id` (and Cloud `transaction_id`) durably before returning from `on_started`.
- Implement `Unknown` recovery — it WILL happen after process restart.

## MUST NOT

- Do not call on AppToApp / PADController in v1 — raises `NotSupported`. Reconcile via merchant records only.

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
val status = sdk.checkStatus(eventId, /*options*/ null)                       // AppToApp/PADController v1: NotSupported
// Cloud:
val opts = CheckStatusOptions.Cloud(CloudCheckStatusOptions(
    merchantId = "MID", securityToken = TOKEN,
    identity = CloudIdentity.Imei("STORE-POS", "IMEI")
))
val s: OperationStatus = sdk.checkStatus(plutusTxnRefId, opts)
```

### Android (Java) — shipping

> Java samples reference `Unsigned.toUInt(...)` / `Unsigned.toULong(...)` from `com.merchant.pos`. See `languages/jvm/setup.md` § 5 for the canonical helper.

```java
OperationStatus status = sdk.checkStatus(eventId, null);
CheckStatusOptions opts = new CheckStatusOptions.Cloud(new CloudCheckStatusOptions(
    "MID", TOKEN, new CloudIdentity.Imei("STORE-POS", "IMEI")));
OperationStatus s = sdk.checkStatus(plutusTxnRefId, opts);
```

### JVM (Kotlin) — shipping

```kotlin
val status = sdk.checkStatus(eventId, /*options*/ null)                       // AppToApp/PADController v1: NotSupported
// Cloud:
val opts = CheckStatusOptions.Cloud(CloudCheckStatusOptions(
    merchantId = "MID", securityToken = TOKEN,
    identity = CloudIdentity.Imei("STORE-POS", "IMEI")
))
val s: OperationStatus = sdk.checkStatus(plutusTxnRefId, opts)
```

### JVM (Java) — shipping

> Java samples reference `Unsigned.toUInt(...)` / `Unsigned.toULong(...)` from `com.merchant.pos`. See `languages/jvm/setup.md` § 5 for the canonical helper.

```java
OperationStatus status = sdk.checkStatus(eventId, null);
CheckStatusOptions opts = new CheckStatusOptions.Cloud(new CloudCheckStatusOptions(
    "MID", TOKEN, new CloudIdentity.Imei("STORE-POS", "IMEI")));
OperationStatus s = sdk.checkStatus(plutusTxnRefId, opts);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
let status = try sdk.checkStatus(eventId: id, options: .cloud(opts))
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
OperationStatus status;
pine_billing_sdk_check_status(sdk, event_id, options_or_null, &status, &err);
```

## Next docs to fetch

- Models: `OperationStatus`, `OperationState`, `CheckStatusOptions`, `CloudCheckStatusOptions`, `CloudTransactionData`, `SdkError`
- Concepts: `eventid-and-reconciliation`, `result-payload`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
