# API: `upload_imei_list`

> **AI INSTRUCTIONS:** This file describes the public method `upload_imei_list` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
UploadImeiListResult upload_imei_list(CloudUploadImeiListOptions options)
```

## Purpose

Cloud admin: register / refresh the IMEI list known to the upstream for a store.

## Returns

`UploadImeiListResult`.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Required field missing.
- **`SdkError.NotSupported`** — Active transport is not Cloud.
- **`SdkError.TransportError` / `Timeout` / `Network` / `ConnectionTimeout` / `ReadTimeout` / `NonSuccessHttp`** — Cloud HTTP-layer failures.

## MUST

- Set active transport to Cloud first (`set_transport(Cloud)`).
- Never log `securityToken`.
- Wrap the call in a background dispatcher (it blocks on HTTPS).

## MUST NOT

- Do not call on AppToApp / PADController — raises `NotSupported`.

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
val opts = CloudUploadImeiListOptions(
    merchantId = "MID",
    securityToken = TOKEN,
    storeId = "STORE-1",
    hardwareId = null,
    imeiList = listOf(CloudImeiListItem(imei = "353…", status = 1)),
)
val result: UploadImeiListResult = sdk.uploadImeiList(opts)
```

### Android (Java) — shipping

```java
CloudUploadImeiListOptions opts = new CloudUploadImeiListOptions(
    "MID", TOKEN, "STORE-1", null,
    java.util.List.of(new CloudImeiListItem("353…", 1))
);
UploadImeiListResult result = sdk.uploadImeiList(opts);
```

### JVM (Kotlin) — shipping

```kotlin
val opts = CloudUploadImeiListOptions(
    merchantId = "MID",
    securityToken = TOKEN,
    storeId = "STORE-1",
    hardwareId = null,
    imeiList = listOf(CloudImeiListItem(imei = "353…", status = 1)),
)
val result: UploadImeiListResult = sdk.uploadImeiList(opts)
```

### JVM (Java) — shipping

```java
CloudUploadImeiListOptions opts = new CloudUploadImeiListOptions(
    "MID", TOKEN, "STORE-1", null,
    java.util.List.of(new CloudImeiListItem("353…", 1))
);
UploadImeiListResult result = sdk.uploadImeiList(opts);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
// speculative — verify when the iOS binding ships
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
# speculative — verify when the Python binding ships
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
// speculative — verify when the Node.js binding ships
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
/* speculative — verify when the C binding ships */
```

## Next docs to fetch

- Models: `CloudUploadImeiListOptions`, `CloudImeiListItem`, `UploadImeiListResult`, `SdkError`
- Concepts: `capabilities`, `error-handling`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
