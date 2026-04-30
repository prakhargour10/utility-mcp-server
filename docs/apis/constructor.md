# API: `constructor`

> **AI INSTRUCTIONS:** This file describes the public method `constructor` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
PineBillingSdk(SdkConfig config, PlatformAppToAppBridge? app_to_app_bridge, PlatformBridge? platform_bridge)
```

## Purpose

Construct the SDK with the given config. Validates ranges and cross-field requirements.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `config` | `SdkConfig` | yes | SDK-wide infrastructure config (timeouts, transport choice, transport sub-configs). |
| `app_to_app_bridge` | `PlatformAppToAppBridge?` | no | Required when AppToApp is configured or any future set_transport(AppToApp) is intended; pass null otherwise. |
| `platform_bridge` | `PlatformBridge?` | no | Required if the active transport (today: PADController) needs a host-managed daemon restart; pass null otherwise. |


## Returns

PineBillingSdk instance.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Config field violates a documented range or cross-field rule (e.g. transport=AppToApp without app_to_app, default_timeout_ms outside 1_000..600_000, bad cloud.base_url).
- **`SdkError.TransportUnavailable`** — Initial transport could not be initialised (e.g. AppToApp transport configured but app_to_app_bridge is null).

## MUST

- Pass exactly one SdkConfig.
- If config.transport == AppToApp, pass a non-null app_to_app_bridge.
- If config.transport == PadController and you intend to call restart(), pass a non-null platform_bridge.
- Construct ONCE per process and reuse the instance — do not construct per transaction.

## MUST NOT

- Do not pass merchant identity here; that lives on TransactionRequest.
- Do not embed credentials, tokens, or PII in SdkConfig.

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
> `sdk.constructor(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `SdkConfig`, `PlatformAppToAppBridge`, `PlatformBridge`, `TransportType`
- Concepts: `overview`, `lifecycle`, `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
