# API: `set_transport`

> **AI INSTRUCTIONS:** This file describes the public method `set_transport` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
set_transport(TransportType kind)
```

## Purpose

Replace the active transport. Disconnects the current transport (if any) before swapping.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `kind` | `TransportType` | yes | Target transport. The matching sub-config MUST be present in `SdkConfig`. |

## Returns

`void`.

## Delivery model

Synchronous (short).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — `kind` requires config that was not provided in `SdkConfig` (e.g. `AppToApp` without `app_to_app`, `Cloud` without `cloud`).
- **`SdkError.NotSupported`** — `Tcp` placeholder in v1.

## MUST

- Configure all sub-configs you might switch to at construction time, even if they're not the initial transport.

## MUST NOT

- Do not call mid-transaction — finish or cancel first.

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✓ |
| Tcp | ✗ `NotSupported` |
| Cloud | ✓ |
| PadController | ✓ |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
sdk.setTransport(TransportType.CLOUD)
```

### Android (Java) — shipping

```java
sdk.setTransport(TransportType.CLOUD);
```

### JVM (Kotlin) — shipping

```kotlin
sdk.setTransport(TransportType.CLOUD)
```

### JVM (Java) — shipping

```java
sdk.setTransport(TransportType.CLOUD);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
try sdk.setTransport(kind: .cloud)
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk.set_transport(TransportType.CLOUD)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
sdk.setTransport(TransportType.CLOUD);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_set_transport(sdk, TRANSPORT_CLOUD, &err);
```

## Next docs to fetch

- Models: `TransportType`, `SdkConfig`
- Concepts: `transports`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
