# API: `discover_terminals`

> **AI INSTRUCTIONS:** This file describes the public method `discover_terminals` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
discover_terminals(DiscoveryListener listener)
```

## Purpose

Scan the active transport for available terminals; results delivered via listener.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `listener` | `DiscoveryListener` | yes | on_terminal_found may fire 0..N times; on_completed XOR on_failure ends the scan. |


## Returns

void.

## Delivery model

Asynchronous via DiscoveryListener.

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport does not support discovery (AppToApp, Cloud).

## MUST

- Always pair returned Terminal objects back to connect() within the same active transport.

## MUST NOT

- Do not call discovery again before previous on_completed/on_failure.

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
sdk.discoverTerminals(object : DiscoveryListener { /* … */ })  // v1: every transport raises NotSupported
```

### Android (Java) — shipping

```java
sdk.discoverTerminals(listener);
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
sdk.discoverTerminals(object : DiscoveryListener { /* … */ })  // v1: every transport raises NotSupported
```

### JVM (Java) — shipping

```java
sdk.discoverTerminals(listener);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.discoverTerminals(listener: listener)
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.discover_terminals(listener)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.discoverTerminals(listener);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_discover_terminals(sdk, &listener, &err);
```

## Next docs to fetch

- Models: `DiscoveryListener`, `Terminal`, `SdkError`
- Concepts: `transports`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
