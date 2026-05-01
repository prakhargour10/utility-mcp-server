# API: `upload_imei_list`

> **AI INSTRUCTIONS:** This file describes the public method `upload_imei_list` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
upload_imei_list(CloudUploadImeiListOptions options) -> UploadImeiListResult
```

## Purpose

Cloud-only admin call: register / refresh the IMEI list known to the upstream for a store.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `options` | `CloudUploadImeiListOptions` | yes | merchant_id, security_token, store_id, optional hardware_id, sequence<CloudImeiListItem>. |


## Returns

UploadImeiListResult{response_code,response_message?}.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.NotSupported`** — Active transport != Cloud.
- **`SdkError.InvalidInput`** — Empty list, malformed fields.
- **`SdkError.Network/Timeout/ConnectionTimeout/ReadTimeout/NonSuccessHttp`** — HTTP failures.

## MUST

- Only call when active transport is Cloud.

## MUST NOT

- Do not log security_token.

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
> `sdk.upload_imei_list(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `CloudUploadImeiListOptions`, `CloudImeiListItem`, `UploadImeiListResult`, `SdkError`
- Concepts: `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
