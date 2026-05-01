# API: `is_connected`

> **AI INSTRUCTIONS:** This file describes the public method `is_connected` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
boolean is_connected()
```

## Purpose

Whether the SDK currently holds an open link to a terminal. AppToApp returns true only mid-call. Cloud returns false (per-call HTTPS). PADController tracks the last probe.

## Returns

`boolean`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- This method does NOT throw.

## MUST

- Treat the value as advisory — between the call and the next op the link can drop.

## MUST NOT

- Do not gate `do_transaction` on `is_connected` for AppToApp / Cloud — they bind per call.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | true mid-call only |
| Tcp | `false` |
| Cloud | `false` (per-call HTTPS) |
| PadController | tracks last probe |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
val connected: Boolean = sdk.isConnected()
```

### Android (Java) — shipping

```java
boolean connected = sdk.isConnected();
```

### JVM (Kotlin) — shipping

```kotlin
val connected: Boolean = sdk.isConnected()
```

### JVM (Java) — shipping

```java
boolean connected = sdk.isConnected();
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
