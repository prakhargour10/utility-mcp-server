# API: `ping`

> **AI INSTRUCTIONS:** This file describes the public method `ping` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
ping()
```

## Purpose

Liveness check on the connected terminal.

## Parameters

_None._


## Returns

void on success.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport (AppToApp, Cloud).
- **`SdkError.NotConnected`** — No link.
- **`SdkError.Timeout`** — No reply within configured timeout.
- **`SdkError.TransportError`** — Mid-stream link failure.

## MUST

_(no positive obligations beyond the signature)_

## MUST NOT

_(no anti-patterns specific to this API)_

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✗ `NotSupported` |
| Tcp | ✗ `NotSupported` |
| Cloud | ✗ `NotSupported` |
| PadController | ✗ `NotSupported` (v1) |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
sdk.ping()
```

### Android (Java) — shipping

```java
sdk.ping();
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
sdk.ping()
```

### JVM (Java) — shipping

```java
sdk.ping();
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.ping()
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.ping()
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.ping();
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_ping(sdk, &err);
```

## Next docs to fetch

- Models: `SdkError`
- Concepts: `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
