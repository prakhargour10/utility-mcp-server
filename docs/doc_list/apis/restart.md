# API: `restart`

> **AI INSTRUCTIONS:** This file describes the public method `restart` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
restart()
```

## Purpose

Request a restart of the upstream service the active transport depends on. Used to recover from upstream-daemon failures without tearing down the SDK.

## Returns

`void`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport has no recoverable upstream daemon (today: AppToApp, Cloud, Tcp).
- **`SdkError.OperationInProgress`** — A listener-style operation is in flight; restart is gated against in-flight work.
- **`SdkError.TransportUnavailable`** — Active transport requires a `PlatformBridge` and none was supplied at construction.
- **`SdkError.TransportError`** — Host bridge dispatched but the restart mechanism itself failed.

## MUST

- On Android, supply an `AndroidSystemBridge(context)` at construction.
- Recovery is verified by the next `connect()` or `do_transaction()` — restart itself is fire-and-forget.

## MUST NOT

- Do not assume the daemon is back online when `restart()` returns — verify by re-attempting a transport call.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✗ `NotSupported` |
| Tcp | ✗ `NotSupported` |
| Cloud | ✗ `NotSupported` |
| PadController | ✓ requires `PlatformBridge` |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
sdk.restart()
```

### Android (Java) — shipping

```java
sdk.restart();
```

### JVM (Kotlin) — shipping

```kotlin
sdk.restart()
```

### JVM (Java) — shipping

```java
sdk.restart();
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

- Models: `PlatformBridge`, `SdkError`
- Concepts: `capabilities`, `error-handling`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
