# API: `get_terminal_info`

> **AI INSTRUCTIONS:** This file describes the public method `get_terminal_info` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
get_terminal_info() -> TerminalInfo
```

## Purpose

Static / diagnostic info about the connected terminal.

## Parameters

_None._


## Returns

TerminalInfo{model?,firmware_version?,serial_number?,battery_percent?}.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport.
- **`SdkError.NotConnected`** — No link.
- **`SdkError.Timeout`** — No reply.
- **`SdkError.TransportError`** — Link failure.

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
val info = sdk.getTerminalInfo()
```

### Android (Java) — shipping

```java
TerminalInfo info = sdk.getTerminalInfo();
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
val info = sdk.getTerminalInfo()
```

### JVM (Java) — shipping

```java
TerminalInfo info = sdk.getTerminalInfo();
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
let info = try sdk.getTerminalInfo()
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
info = sdk.get_terminal_info()
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
const info = sdk.getTerminalInfo();
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_get_terminal_info(sdk, &out, &err);
```

## Next docs to fetch

- Models: `TerminalInfo`, `SdkError`
- Concepts: `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
