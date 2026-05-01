# API: `test_print`

> **AI INSTRUCTIONS:** This file describes the public method `test_print` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
test_print(TestPrintListener listener)
```

## Purpose

Print a no-op test slip on the terminal's printer.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `listener` | `TestPrintListener` | yes | Same lifecycle contract as TransactionListener. |


## Returns

void (result delivered via listener).

## Delivery model

Asynchronous via TestPrintListener.

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport.
- **`SdkError.NotConnected`** — No link.
- **`SdkError.OperationInProgress`** — Concurrent op.
- **`SdkError.TransportUnavailable`** — Cannot bind.

## MUST

_(no positive obligations beyond the signature)_

## MUST NOT

_(no anti-patterns specific to this API)_

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✓ |
| Tcp | ✗ `NotSupported` |
| Cloud | ✗ `NotSupported` |
| PadController | ✗ `NotSupported` (v1) |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
sdk.testPrint(object : TestPrintListener {
    override fun onStarted(eventId: String) { /* … */ }
    override fun onSuccess(eventId: String) { /* … */ }
    override fun onFailure(error: SdkException) { /* … */ }
})
```

### Android (Java) — shipping

```java
sdk.testPrint(new TestPrintListener() { /* … */ });
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
sdk.testPrint(object : TestPrintListener {
    override fun onStarted(eventId: String) { /* … */ }
    override fun onSuccess(eventId: String) { /* … */ }
    override fun onFailure(error: SdkException) { /* … */ }
})
```

### JVM (Java) — shipping

```java
sdk.testPrint(new TestPrintListener() { /* … */ });
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.testPrint(listener: listener)
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.test_print(listener)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.testPrint(listener);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_test_print(sdk, &listener, &err);
```

## Next docs to fetch

- Models: `TestPrintListener`, `SdkError`
- Concepts: `lifecycle`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
