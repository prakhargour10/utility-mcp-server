# API: `disconnect`

> **AI INSTRUCTIONS:** This file describes the public method `disconnect` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
disconnect()
```

## Purpose

Release the link. Idempotent on already-disconnected.

## Parameters

_None._


## Returns

void.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.TransportError`** — Failure tearing down the underlying socket / IPC link.

## MUST

- Always call before discarding the SDK instance.

## MUST NOT

_(no anti-patterns specific to this API)_

## Transport support matrix

| Transport | Behaviour |
|---|---|
| AppToApp | no-op (the upstream PoS service is bound per call). |
| Tcp | ✗ `NotSupported` (v1 placeholder). |
| Cloud | no-op (HTTPS is per-call). |
| PadController | tears down probe state; idempotent on already-disconnected. |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
sdk.disconnect()
```

### Android (Java) — shipping

```java
sdk.disconnect();
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
sdk.disconnect()
```

### JVM (Java) — shipping

```java
sdk.disconnect();
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.disconnect()
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.disconnect()
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.disconnect();
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_disconnect(sdk, &err);
```

## Next docs to fetch

- Models: `SdkError`
- Concepts: `lifecycle`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
