# API: `connect`

> **AI INSTRUCTIONS:** This file describes the public method `connect` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
connect(Terminal terminal)
```

## Purpose

Establish the link to the given terminal. No-op for AppToApp / Cloud (which bind per call).

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `terminal` | `Terminal` | yes | Must have terminal.transport == active transport. |


## Returns

void.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — terminal.transport != active.
- **`SdkError.NotSupported`** — Active transport has no discovery/connection model.
- **`SdkError.TransportUnavailable`** — Could not reach the terminal.

## MUST

- Always pass a Terminal returned by discover_terminals on the same active transport.

## MUST NOT

- Do not construct a Terminal by hand for transports that require discovery.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | no-op (binds per call) |
| Tcp | ✗ `NotSupported` (v1 placeholder) |
| Cloud | no-op (HTTPS per call) |
| PadController | ✓ probe-style |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
sdk.connect(terminal)
```

### Android (Java) — shipping

```java
sdk.connect(terminal);
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
sdk.connect(terminal)
```

### JVM (Java) — shipping

```java
sdk.connect(terminal);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.connect(terminal: terminal)
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.connect(terminal=terminal)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.connect(terminal);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_connect(sdk, &terminal, &err);
```

## Next docs to fetch

- Models: `Terminal`, `TransportType`, `SdkError`
- Concepts: `transports`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
