# API: `run_self_test`

> **AI INSTRUCTIONS:** This file describes the public method `run_self_test` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
SelfTestResult run_self_test()
```

## Purpose

Trigger a terminal self-test and wait for the result.

## Returns

`SelfTestResult`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — All v1 transports raise this.
- **`SdkError.NotConnected`** — No active link.

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
val result: SelfTestResult = sdk.runSelfTest()
```

### Android (Java) — shipping

```java
SelfTestResult result = sdk.runSelfTest();
```

### JVM (Kotlin) — shipping

```kotlin
val result: SelfTestResult = sdk.runSelfTest()
```

### JVM (Java) — shipping

```java
SelfTestResult result = sdk.runSelfTest();
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

- Models: `SelfTestResult`, `SdkError`
- Concepts: `capabilities`, `error-handling`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
