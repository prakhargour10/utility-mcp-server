# API: `discover_terminals`

> **AI INSTRUCTIONS:** This file describes the public method `discover_terminals` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
discover_terminals(DiscoveryListener listener)
```

## Purpose

Scan the active transport for available terminals; results delivered via listener.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `listener` | `DiscoveryListener` | yes | on_terminal_found may fire 0..N times; on_completed XOR on_failure ends the scan. |


## Returns

void.

## Delivery model

Asynchronous via DiscoveryListener.

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport does not support discovery (AppToApp, Cloud).

## MUST

- Always pair returned Terminal objects back to connect() within the same active transport.

## MUST NOT

- Do not call discovery again before previous on_completed/on_failure.

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
> `sdk.discover_terminals(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `DiscoveryListener`, `Terminal`, `SdkError`
- Concepts: `transports`, `capabilities`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
