# API: `get_logs`

> **AI INSTRUCTIONS:** This file describes the public method `get_logs` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
get_logs() -> TerminalLogs
```

## Purpose

Pull a snapshot of terminal-side logs.

## Parameters

_None._


## Returns

TerminalLogs{lines[]} — raw lines as the terminal reported them.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport.
- **`SdkError.NotConnected`** — No link.
- **`SdkError.Timeout`** — No reply.
- **`SdkError.TransportError`** — Link failure.

## MUST

- Treat lines as opaque diagnostic strings.

## MUST NOT

- Do not parse for PII; assume content is safe-by-source but never leak verbatim to end users.

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
val logs: TerminalLogs = sdk.getLogs()
```

### Android (Java) — shipping

```java
TerminalLogs logs = sdk.getLogs();
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
val logs: TerminalLogs = sdk.getLogs()
```

### JVM (Java) — shipping

```java
TerminalLogs logs = sdk.getLogs();
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
let logs = try sdk.getLogs()
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
logs = sdk.get_logs()
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
const logs = sdk.getLogs();
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_get_logs(sdk, &out, &err);
```

## Next docs to fetch

- Models: `TerminalLogs`, `SdkError`
- Concepts: `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
