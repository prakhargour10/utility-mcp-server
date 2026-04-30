# API: `set_transport`

> **AI INSTRUCTIONS:** This file describes the public method `set_transport` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
set_transport(TransportType kind)
```

## Purpose

Replace the active transport. Disconnects current transport first.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `kind` | `TransportType` | yes | Must be one for which the SdkConfig provided the matching sub-config (e.g. AppToApp requires app_to_app). |


## Returns

void.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Required sub-config missing.

## MUST

- Provide the matching sub-config in SdkConfig at construction time for any transport you may switch to later.

## MUST NOT

- Do not call mid-transaction.

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
> `sdk.set_transport(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `TransportType`, `SdkConfig`
- Concepts: `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
