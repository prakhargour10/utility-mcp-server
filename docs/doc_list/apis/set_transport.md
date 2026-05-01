# API: `set_transport`

> **AI INSTRUCTIONS:** This file describes the public method `set_transport` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
set_transport(TransportType kind)
```

## Purpose

Replace the active transport. Disconnects current transport first.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `kind` | `TransportType` | yes | Must be one for which the SdkConfig provided the matching sub-config (e.g. AppToApp requires app_to_app). |


## Returns

void.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Required sub-config missing.

## MUST

- Provide the matching sub-config in SdkConfig at construction time for any transport you may switch to later.

## MUST NOT

- Do not call mid-transaction.

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
sdk.setTransport(TransportType.CLOUD)
```

### Android (Java) — shipping

```java
sdk.setTransport(TransportType.CLOUD);
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
sdk.setTransport(TransportType.CLOUD)
```

### JVM (Java) — shipping

```java
sdk.setTransport(TransportType.CLOUD);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.setTransport(kind: .cloud)
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.set_transport(TransportType.CLOUD)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.setTransport(TransportType.Cloud);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_set_transport(sdk, PINE_TRANSPORT_CLOUD, &err);
```

## Next docs to fetch

- Models: `TransportType`, `SdkConfig`
- Concepts: `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
