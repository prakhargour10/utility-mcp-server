# API: `is_connected`

> **AI INSTRUCTIONS:** This file describes the public method `is_connected` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
is_connected() -> boolean
```

## Purpose

Whether the SDK currently holds an open link. Per-transport semantics vary.

## Parameters

_None._


## Returns

boolean. AppToApp: true only mid-call. TCP/Cloud/PADController: true between successful connect and next disconnect/transport failure. No transport selected: false.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

_None._

## MUST

- Use as a UI hint, not a guarantee for the next call (state may change by the time you call do_transaction).

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
> `sdk.is_connected(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `TransportType`
- Concepts: `lifecycle`, `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
