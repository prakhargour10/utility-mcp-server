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

## Android binding override (façade)

The Android binding ships a thin Kotlin façade in
`com.pinelabs.billing.sdk.PineBillingSdk` that wraps the UDL constructor
to:

* take an Android `Context` (needed to bind the upstream PoS service for
  the AppToApp transport),
* auto-build the `MasterAppTransport` (the `PlatformAppToAppBridge`
  implementation) from the `SdkConfig.app_to_app` and
  `SdkConfig.application_id` fields when AppToApp is the configured
  transport,
* enforce a main-thread guard: every blocking method throws
  `IllegalStateException` if invoked on the Android main thread.

### Façade signature

```kotlin
package com.pinelabs.billing.sdk

class PineBillingSdk @JvmOverloads constructor(
    context: Context,
    config: SdkConfig,
    platformBridge: PlatformBridge? = null,
) : AutoCloseable
```

* `context` — application context is held internally; passing an
  Activity is safe.
* `config` — same `uniffi.pine_billing.SdkConfig` as on the JVM
  binding.
* `platformBridge` — optional. Required only if you intend to call
  `restart()` on a PADController-routed SDK; pass an
  `AndroidSystemBridge` then. AppToApp / Cloud-only deployments may
  pass `null`.

> **`PlatformAppToAppBridge` is NOT a parameter of the Android façade.**
> The façade builds it for you from `config`. On other bindings (JVM,
> ios, python, …) the merchant supplies the bridge explicitly.


## MUST

- Pass exactly one SdkConfig.
- If config.transport == AppToApp, pass a non-null app_to_app_bridge.
- If config.transport == PadController and you intend to call restart(), pass a non-null platform_bridge.
- Construct ONCE per process and reuse the instance — do not construct per transaction.

## MUST NOT

- Do not pass merchant identity here; that lives on TransactionRequest.
- Do not embed credentials, tokens, or PII in SdkConfig.

## Per-language call shapes

### Android (Kotlin) — shipping

```kotlin
val config = SdkConfig(
    defaultTimeoutMs = 60_000u,
    transport = TransportType.APP_TO_APP,
    appToApp = AppToAppConfig(userId = "POS-USER", version = "1.0"),
    applicationId = BuildConfig.PINELABS_APP_ID,
)
// Android façade — Context required; AppToApp bridge is auto-built.
val sdk = PineBillingSdk(context, config, /*platformBridge*/ null)
```

### Android (Java) — shipping

```java
SdkConfig config = new SdkConfig(
    /*defaultTimeoutMs*/ Integers.toUInt(60_000),
    /*logLevel*/ null,
    TransportType.APP_TO_APP,
    new AppToAppConfig("POS-USER", "1.0"),
    BuildConfig.PINELABS_APP_ID,
    /*cloud*/ null,
    /*padController*/ null
);
// Android façade.
PineBillingSdk sdk = new PineBillingSdk(context, config, /*platformBridge*/ null);
```

### JVM (Kotlin) — shipping

> The JVM binding does NOT ship a façade; call the UniFFI-generated
> class directly. There is no Android `Context` and no main-thread
> guard.

```kotlin
import uniffi.pine_billing.PineBillingSdk
// JVM has no Context; instantiate the UniFFI class directly.
val sdk = PineBillingSdk(config, /*appToAppBridge*/ null, /*platformBridge*/ null)
```

### JVM (Java) — shipping

```java
import uniffi.pine_billing.PineBillingSdk;
PineBillingSdk sdk = new PineBillingSdk(config, /*appToAppBridge*/ null, /*platformBridge*/ null);
```

### Swift (iOS) — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```swift
let sdk = try PineBillingSdk(config: config, appToAppBridge: nil, platformBridge: nil)
```

### Python — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```python
sdk = PineBillingSdk(config=config, app_to_app_bridge=None, platform_bridge=None)
```

### Node.js — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```javascript
const sdk = new PineBillingSdk(config, /*appToAppBridge*/null, /*platformBridge*/null);
```

### C — roadmap

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

```c
PineBillingSdk* sdk = pine_billing_sdk_new(&config, NULL, NULL, &err);
```

## Next docs to fetch

- Models: `SdkConfig`, `PlatformAppToAppBridge`, `PlatformBridge`, `TransportType`
- Concepts: `overview`, `lifecycle`, `transports`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
