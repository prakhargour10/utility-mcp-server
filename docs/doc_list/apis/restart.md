# API: `restart`

> **AI INSTRUCTIONS:** This file describes the public method `restart` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
restart()
```

## Purpose

Request a restart of the upstream service the active transport depends on. Fire-and-forget.

## Parameters

_None._


## Returns

void on dispatched.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport has no restartable upstream daemon (AppToApp, Cloud).
- **`SdkError.OperationInProgress`** — In-flight listener op.
- **`SdkError.TransportUnavailable`** — PlatformBridge missing.
- **`SdkError.TransportError`** — Bridge dispatched but mechanism failed.

## MUST

- Verify recovery via the next connect() / do_transaction().

## MUST NOT

_(no anti-patterns specific to this API)_

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✗ `NotSupported` |
| Tcp | ✗ `NotSupported` |
| Cloud | ✗ `NotSupported` |
| PadController | ✓ — requires `PlatformBridge` |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
// PADController only — requires AndroidSystemBridge at construction.
sdk.restart()
```

### Android (Java) — shipping

```java
sdk.restart();
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
// PADController only — requires AndroidSystemBridge at construction.
sdk.restart()
```

### JVM (Java) — shipping

```java
sdk.restart();
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.restart()
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.restart()
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.restart();
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_restart(sdk, &err);
```

## Next docs to fetch

- Models: `PlatformBridge`, `SdkError`
- Concepts: `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
