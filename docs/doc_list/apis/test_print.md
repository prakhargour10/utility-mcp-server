# API: `test_print`

> **AI INSTRUCTIONS:** This file describes the public method `test_print` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
test_print(TestPrintListener listener)
```

## Purpose

Print a no-op test slip on the terminal's printer. Useful for installation validation and printer-paper checks. Allocates an `event_id` and delivers result via listener.

## Returns

`void`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Listener invariants violated.
- **`SdkError.OperationInProgress`** — Concurrent op.
- **`SdkError.NotSupported`** — Active transport does not support test_print (today: only AppToApp).
- **`SdkError.TransportUnavailable`** — Active transport cannot be reached.

## MUST

- Disable trigger control on `onStarted`, re-enable on terminal-state callback.
- On Android, dispatch off the main thread.

## MUST NOT

- Do not block in any callback.

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
sdk.testPrint(new TestPrintListener() {
    @Override public void onStarted(String e) { }
    @Override public void onSuccess(String e) { }
    @Override public void onFailure(SdkException ex) { }
});
```

### JVM (Kotlin) — shipping

```kotlin
sdk.testPrint(object : TestPrintListener {
    override fun onStarted(eventId: String) { /* … */ }
    override fun onSuccess(eventId: String) { /* … */ }
    override fun onFailure(error: SdkException) { /* … */ }
})
```

### JVM (Java) — shipping

```java
sdk.testPrint(new TestPrintListener() {
    @Override public void onStarted(String e) { }
    @Override public void onSuccess(String e) { }
    @Override public void onFailure(SdkException ex) { }
});
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

- Models: `TestPrintListener`, `SdkError`
- Concepts: `threading`, `lifecycle`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
