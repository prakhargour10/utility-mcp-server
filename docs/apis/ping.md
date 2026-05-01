# API: `ping`

> **AI INSTRUCTIONS:** This file describes the public method `ping` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
ping()
```

## Purpose

Liveness check on the connected terminal.

## Parameters

_None._


## Returns

void on success.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport (AppToApp, Cloud).
- **`SdkError.NotConnected`** — No link.
- **`SdkError.Timeout`** — No reply within configured timeout.
- **`SdkError.TransportError`** — Mid-stream link failure.

## MUST

_(no positive obligations beyond the signature)_

## MUST NOT

_(no anti-patterns specific to this API)_

## Per-language call shape

```kotlin
// Kotlin
val sdk = PineBillingSdk(config, /*appToAppBridge*/null, /*platformBridge*/null)
```
```swift
// Swift
let sdk = try PineBillingSdk(config: config, appToAppBridge: nil, platformBridge: nil)
```
```python
# Python
sdk = PineBillingSdk(config=config, app_to_app_bridge=None, platform_bridge=None)
```
```javascript
// Node.js
const sdk = new PineBillingSdk(config, /*appToAppBridge*/null, /*platformBridge*/null);
```
```c
/* C */
PineBillingSdk* sdk = pine_billing_sdk_new(&config, NULL, NULL, &err);
```
> The above is the constructor shape; for non-constructor APIs use
> `sdk.ping(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `SdkError`
- Concepts: `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
