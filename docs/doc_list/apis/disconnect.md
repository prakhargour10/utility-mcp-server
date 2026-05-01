# API: `disconnect`

> **AI INSTRUCTIONS:** This file describes the public method `disconnect` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
disconnect()
```

## Purpose

Release the link. Idempotent on already-disconnected.

## Returns

`void`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.TransportError`** — Mid-stream disconnect failure (rare).

## MUST

- Wrap the call in a platform-idiomatic background dispatcher (Android: `Dispatchers.IO`).

## MUST NOT

- Do not call from the Android main thread — the façade throws.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | no-op |
| Tcp | ✗ `NotSupported` |
| Cloud | no-op |
| PadController | ✓ |

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

- Models: `SdkError`
- Concepts: `lifecycle`, `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
