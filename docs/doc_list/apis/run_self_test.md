# API: `run_self_test`

> **AI INSTRUCTIONS:** This file describes the public method `run_self_test` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
run_self_test() -> SelfTestResult
```

## Purpose

Trigger a terminal self-test and wait for the result.

## Parameters

_None._


## Returns

SelfTestResult{passed, details[]}.

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
val r: SelfTestResult = sdk.runSelfTest()
```

### Android (Java) — shipping

```java
SelfTestResult r = sdk.runSelfTest();
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
val r: SelfTestResult = sdk.runSelfTest()
```

### JVM (Java) — shipping

```java
SelfTestResult r = sdk.runSelfTest();
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
let r = try sdk.runSelfTest()
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
r = sdk.run_self_test()
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
const r = sdk.runSelfTest();
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_run_self_test(sdk, &out, &err);
```

## Next docs to fetch

- Models: `SelfTestResult`, `SdkError`
- Concepts: `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
