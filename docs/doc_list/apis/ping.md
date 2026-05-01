# API: `ping`

> **AI INSTRUCTIONS:** This file describes the public method `ping` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
ping()
```

## Purpose

Liveness check. Returns successfully if the terminal responded within the configured timeout.

## Returns

`void`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — All v1 transports raise this.

## MUST

- Skip in v1 — every transport raises NotSupported.

## MUST NOT

- Do not call from the Android main thread — the façade throws.

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
- Concepts: `capabilities`, `error-handling`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
