# API: `restart`

> **AI INSTRUCTIONS:** This file describes the public method `restart` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
restart()
```

## Purpose

Request a restart of the upstream service the active transport depends on. Fire-and-forget.

## Parameters

_None._


## Returns

void on dispatched.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport has no restartable upstream daemon (AppToApp, Cloud).
- **`SdkError.OperationInProgress`** — In-flight listener op.
- **`SdkError.TransportUnavailable`** — PlatformBridge missing.
- **`SdkError.TransportError`** — Bridge dispatched but mechanism failed.

## MUST

- Verify recovery via the next connect() / do_transaction().

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
> `sdk.restart(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `PlatformBridge`, `SdkError`
- Concepts: `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
