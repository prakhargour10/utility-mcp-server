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

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✗ `NotSupported` |
| Tcp | ✗ `NotSupported` |
| Cloud | ✓ |
| PadController | ✗ `NotSupported` |

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
val r = sdk.uploadImeiList(CloudUploadImeiListOptions(
    merchantId = "MID", securityToken = TOKEN, storeId = "STORE",
    hardwareId = null,
    imeiList = listOf(CloudImeiListItem(imei = "353…", status = 1)),
))
```

### Android (Java) — shipping

```java
UploadImeiListResult r = sdk.uploadImeiList(opts);
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
val r = sdk.uploadImeiList(CloudUploadImeiListOptions(
    merchantId = "MID", securityToken = TOKEN, storeId = "STORE",
    hardwareId = null,
    imeiList = listOf(CloudImeiListItem(imei = "353…", status = 1)),
))
```

### JVM (Java) — shipping

```java
UploadImeiListResult r = sdk.uploadImeiList(opts);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
let r = try sdk.uploadImeiList(options: opts)
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
r = sdk.upload_imei_list(opts)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
const r = sdk.uploadImeiList(opts);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
pine_billing_sdk_upload_imei_list(sdk, &opts, &out, &err);
```

## Next docs to fetch

- Models: `CloudUploadImeiListOptions`, `CloudImeiListItem`, `UploadImeiListResult`, `SdkError`
- Concepts: `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
