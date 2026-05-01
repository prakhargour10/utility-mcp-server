# API: `constructor`

> **AI INSTRUCTIONS:** This file describes the public method `constructor` on `PineBillingSdk`. Read it before emitting any code that calls this method. Validation rules and error semantics are normative.

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
| `app_to_app_bridge` | `PlatformAppToAppBridge?` | no | Required when AppToApp is configured or any future `set_transport(AppToApp)` is intended; pass `null` otherwise. **Android façade hides this param** — see "Android façade" section below. |
| `platform_bridge` | `PlatformBridge?` | no | Required if the active transport (today: PADController) needs a host-managed daemon restart; pass `null` otherwise. |

## Returns

`PineBillingSdk` instance.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Config field violates a documented range or cross-field rule (e.g. `transport=AppToApp` without `app_to_app`, `default_timeout_ms` outside 1_000..600_000, bad `cloud.base_url`).
- **`SdkError.TransportUnavailable`** — Initial transport could not be initialised (e.g. AppToApp transport configured but `app_to_app_bridge` is null).

## Android façade (binding override)

The Android binding ships a thin Kotlin façade in `com.pinelabs.billing.sdk.PineBillingSdk` that wraps the UDL constructor:

* takes an Android `Context` (needed to bind the upstream PoS service for the AppToApp transport),
* auto-builds the `MasterAppTransport` (the `PlatformAppToAppBridge` implementation) from `SdkConfig.app_to_app` and `SdkConfig.application_id` when AppToApp is the configured transport,
* enforces a main-thread guard: every blocking method throws `IllegalStateException` if invoked on the Android main thread.

### Façade signature

```kotlin
package com.pinelabs.billing.sdk

class PineBillingSdk @JvmOverloads constructor(
    context: Context,
    config: SdkConfig,
    platformBridge: PlatformBridge? = null,
) : AutoCloseable
```

> **`PlatformAppToAppBridge` is NOT a parameter of the Android façade.** The façade builds it for you from `config`. On other bindings (JVM, ios, python, …) the merchant supplies the bridge explicitly (or, on JVM, AppToApp is unavailable).

## MUST

### UDL canonical

- Pass exactly one `SdkConfig`.
- If `config.transport == AppToApp`, pass a non-null `app_to_app_bridge`.
- If `config.transport == PadController` and you intend to call `restart()`, pass a non-null `platform_bridge`.
- Construct ONCE per process and reuse the instance — do not construct per transaction.

### Android façade

- Pass an Android `Context` (application context recommended; the façade extracts it).
- Configure `SdkConfig.app_to_app` + `SdkConfig.application_id` for AppToApp; the façade builds the bridge for you.
- Pass an `AndroidSystemBridge` as `platformBridge` only if you intend to call `restart()`.
- Provision `applicationId` from a non-VCS secrets file via `BuildConfig.PINELABS_APP_ID`. Sandbox value: `1001`.

## MUST NOT

### UDL canonical

- Do not pass merchant identity here; that lives on `TransactionRequest`.
- Do not embed credentials, tokens, or PII in `SdkConfig`.

### Android façade

- Do not call from the Android main thread inside a synchronous test — construction itself is short, but the façade holds a reference to the application context for later use.
- Do not pass `BuildConfig.PINELABS_APP_ID` if it might be empty/null — fail fast at configure-time. See `languages/android/integration.md` § "applicationId provisioning".

## Transport support matrix

| Transport | v1 behaviour |
|---|---|
| AppToApp | ✓ — requires `app_to_app_bridge` (Android façade auto-builds) |
| Tcp | placeholder — set as initial transport raises `NotSupported` on first call |
| Cloud | ✓ — requires `cloud: CloudConfig` |
| PadController | ✓ — `pad_controller: PadControllerConfig` honoured |

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

> Java samples reference `Unsigned.toUInt(...)` / `Unsigned.toULong(...)` from `com.merchant.pos`. See `languages/jvm/setup.md` § 5 for the canonical helper.

```java
SdkConfig config = new SdkConfig(
    /*defaultTimeoutMs*/ Unsigned.toUInt(60_000L),
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

> The JVM binding does NOT ship a façade. AppToApp is unavailable on JVM — use Cloud or PADController.

```kotlin
import uniffi.pine_billing.PineBillingSdk
val sdk = PineBillingSdk(config, /*appToAppBridge*/ null, /*platformBridge*/ null)
```

### JVM (Java) — shipping

> Java samples reference `Unsigned.toUInt(...)` / `Unsigned.toULong(...)` from `com.merchant.pos`. See `languages/jvm/setup.md` § 5 for the canonical helper.

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
- Languages: `languages/android/setup`, `languages/jvm/setup`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method (see capability matrix in `concepts/capabilities.md`), refuse to emit the call and ask the user to switch transport.
