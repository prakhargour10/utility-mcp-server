# API: `discover_terminals`

> **AI INSTRUCTIONS:** This file describes the public method `discover_terminals` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
discover_terminals(DiscoveryListener listener)
```

## Purpose

Scan the active transport for available terminals; result is delivered via listener.

## Returns

`void`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — All transports in v1 raise this. Discovery is a roadmap capability.

## MUST

- Do not generate calls to this method in v1 — every transport raises NotSupported.

## MUST NOT

- Do not assume PADController will discover Bluetooth terminals — it does not in v1.

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
sdk.discoverTerminals(object : DiscoveryListener {
    override fun onTerminalFound(terminal: Terminal) { /* … */ }
    override fun onCompleted() { /* … */ }
    override fun onFailure(error: SdkException) { /* … */ }
})
```

### Android (Java) — shipping

```java
sdk.discoverTerminals(new DiscoveryListener() {
    @Override public void onTerminalFound(Terminal t) { }
    @Override public void onCompleted() { }
    @Override public void onFailure(SdkException e) { }
});
```

### JVM (Kotlin) — shipping

```kotlin
sdk.discoverTerminals(object : DiscoveryListener {
    override fun onTerminalFound(terminal: Terminal) { /* … */ }
    override fun onCompleted() { /* … */ }
    override fun onFailure(error: SdkException) { /* … */ }
})
```

### JVM (Java) — shipping

```java
sdk.discoverTerminals(new DiscoveryListener() {
    @Override public void onTerminalFound(Terminal t) { }
    @Override public void onCompleted() { }
    @Override public void onFailure(SdkException e) { }
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

- Models: `DiscoveryListener`, `Terminal`, `TransportType`, `SdkError`
- Concepts: `capabilities`, `transports`, `threading`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
