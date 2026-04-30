# API: `connect`

> **AI INSTRUCTIONS:** This file describes the public method `connect` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
connect(Terminal terminal)
```

## Purpose

Establish the link to the given terminal. No-op for AppToApp / Cloud (which bind per call).

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `terminal` | `Terminal` | yes | Must have terminal.transport == active transport. |


## Returns

void.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — terminal.transport != active.
- **`SdkError.NotSupported`** — Active transport has no discovery/connection model.
- **`SdkError.TransportUnavailable`** — Could not reach the terminal.

## MUST

- Always pass a Terminal returned by discover_terminals on the same active transport.

## MUST NOT

- Do not construct a Terminal by hand for transports that require discovery.

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
> `sdk.connect(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `Terminal`, `TransportType`, `SdkError`
- Concepts: `transports`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
