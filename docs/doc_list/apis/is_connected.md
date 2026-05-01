# API: `is_connected`

> **AI INSTRUCTIONS:** This file describes the public method `is_connected` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
is_connected() -> boolean
```

## Purpose

Whether the SDK currently holds an open link. Per-transport semantics vary.

## Parameters

_None._


## Returns

boolean. AppToApp: true only mid-call. TCP/Cloud/PADController: true between successful connect and next disconnect/transport failure. No transport selected: false.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

_None._

## MUST

- Use as a UI hint, not a guarantee for the next call (state may change by the time you call do_transaction).

## MUST NOT

_(no anti-patterns specific to this API)_

## Transport support matrix

| Transport | Behaviour |
|---|---|
| AppToApp | `true` only while a call is in flight (binds upstream PoS service per call). |
| Tcp | `false` (v1 placeholder — no transport selected behaviour). |
| Cloud | `false` between calls (HTTPS per-call). |
| PadController | tracks the last `connect()` probe result. |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
val ok: Boolean = sdk.isConnected()
```

### Android (Java) — shipping

```java
boolean ok = sdk.isConnected();
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
val ok: Boolean = sdk.isConnected()
```

### JVM (Java) — shipping

```java
boolean ok = sdk.isConnected();
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
let ok: Bool = sdk.isConnected()
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
ok = sdk.is_connected()
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
const ok = sdk.isConnected();
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
bool ok = pine_billing_sdk_is_connected(sdk);
```

## Next docs to fetch

- Models: `TransportType`
- Concepts: `lifecycle`, `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
