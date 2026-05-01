# API: `connect`

> **AI INSTRUCTIONS:** This file describes the public method `connect` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
connect(Terminal terminal)
```

## Purpose

Establish the link to the given terminal. Required by transports that have a separate connect step (PADController, future BT/USB/TCP) and a no-op for transports that bind per-call (AppToApp, Cloud).

## Returns

`void`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — `terminal.transport` is not the active transport.
- **`SdkError.NotSupported`** — Active transport does not support discovery / connection (today: not raised by AppToApp / Cloud — they no-op; PADController accepts; Tcp placeholder).
- **`SdkError.TransportError`** — Probe failed.

## MUST

- Wrap the call in a platform-idiomatic background dispatcher (Android: `Dispatchers.IO`).

## MUST NOT

- Do not call from the Android main thread — the façade throws.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | no-op (binds per call) |
| Tcp | ✗ `NotSupported` |
| Cloud | no-op (HTTPS per call) |
| PadController | ✓ probe-only |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
val terminal = Terminal(id = "127.0.0.1:8082", transport = TransportType.PAD_CONTROLLER, displayName = null, model = null, serialNumber = null)
sdk.connect(terminal)
```

### Android (Java) — shipping

```java
Terminal terminal = new Terminal("127.0.0.1:8082", TransportType.PAD_CONTROLLER, null, null, null);
sdk.connect(terminal);
```

### JVM (Kotlin) — shipping

```kotlin
val terminal = Terminal(id = "127.0.0.1:8082", transport = TransportType.PAD_CONTROLLER, displayName = null, model = null, serialNumber = null)
sdk.connect(terminal)
```

### JVM (Java) — shipping

```java
Terminal terminal = new Terminal("127.0.0.1:8082", TransportType.PAD_CONTROLLER, null, null, null);
sdk.connect(terminal);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
// speculative — verify when the iOS binding ships
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
# speculative — verify when the Python binding ships
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
// speculative — verify when the Node.js binding ships
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
/* speculative — verify when the C binding ships */
```

## Next docs to fetch

- Models: `Terminal`, `TransportType`, `SdkError`
- Concepts: `transports`, `capabilities`, `lifecycle`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
