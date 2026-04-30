# Language: Android (Kotlin)

> **AI INSTRUCTIONS:** Use this file when TARGET_LANGUAGE = `android`. It contains the complete environment, distribution, and integration steps. Do not invent gradle coordinates or import paths.

## Distribution

- **Artifact:** `pine-billing-sdk-<version>.aar`
- **Public package:** `com.pinelabs.billing.sdk`
- **Generated UniFFI package:** `uniffi.pine_billing` (do NOT import directly in user code)
- **Native lib inside the AAR:** `libpine_billing_sdk.so` for `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`
- **Download:** call `get_sdk(artifact_key="android-aar")`

## Environment requirements

| Item | Required |
|---|---|
| Android Gradle Plugin | 8.0+ |
| Kotlin | 1.9+ |
| `compileSdk` | 34+ |
| `minSdk` | 24 (Android 7.0) |
| Pinelabs MasterApp installed (for AppToApp transport only) | yes |
| Internet permission (for Cloud transport only) | yes |

## Setup

### 1. Add the AAR

```kotlin
// app/build.gradle.kts
android {
    namespace = "com.merchant.pos"
    compileSdk = 34
    defaultConfig { minSdk = 24 }
    packaging {
        jniLibs.useLegacyPackaging = false
        // Avoid duplicate libc++_shared.so collisions
        jniLibs.pickFirsts += setOf("**/libc++_shared.so")
    }
}

dependencies {
    implementation(files("libs/pine-billing-sdk-<version>.aar"))
    implementation("net.java.dev.jna:jna:5.14.0@aar")
}
```

Place the AAR under `app/libs/`.

### 2. Manifest

```xml
<!-- AppToApp transport: no extra permissions; ensures MasterApp is installed -->
<queries>
  <package android:name="com.pinelabs.masterapp" />
</queries>

<!-- Cloud transport -->
<uses-permission android:name="android.permission.INTERNET" />
```

### 3. ProGuard / R8

```proguard
# UniFFI generated bindings
-keep class uniffi.pine_billing.** { *; }
-keep class com.pinelabs.billing.sdk.** { *; }
-keepclassmembers class ** implements com.pinelabs.billing.sdk.* { *; }
```

## AppToApp bridge

For TARGET_TRANSPORT = AppToApp the SDK requires a `PlatformAppToAppBridge` implementation that wraps Pinelabs MasterApp Messenger IPC. The merchant's Android binding ships a stock implementation; instantiate it once and pass it to `PineBillingSdk(...)`.

## SDK construction

```kotlin
import com.pinelabs.billing.sdk.PineBillingSdk
import com.pinelabs.billing.sdk.SdkConfig
import com.pinelabs.billing.sdk.AppToAppConfig
import com.pinelabs.billing.sdk.TransportType

val config = SdkConfig(
    defaultTimeoutMs = 60_000u,
    transport = TransportType.APP_TO_APP,
    appToApp = AppToAppConfig(userId = "POS-USER", version = "1.0"),
    applicationId = BuildConfig.PINELABS_APP_ID,
)
val sdk = PineBillingSdk(config, MasterAppMessengerBridge(context), /*platformBridge*/ null)
```

## Threading

- All listener callbacks fire on an SDK worker thread.
- ALWAYS marshal to the UI thread for widget updates:

```kotlin
override fun onSuccess(result: TransactionResult) {
    Handler(Looper.getMainLooper()).post { /* update UI */ }
}
```

## Code-generation directives for the LLM

- Always emit `try`/`catch` blocks around `do_transaction`, `cancel`, `check_status`, `set_transport`. Catch `SdkError` and dispatch by variant (use Kotlin sealed-class-style `when`).
- Disable the trigger button in `onStarted`, re-enable in `onSuccess` / `onFailure`.
- Never log `request.metadata`, `result.maskedPan` (except at debug), `cloud.securityToken`, or any field tagged "Never log".
- For `applicationId`, read it from a `BuildConfig` field populated from a non-VCS secrets file — never inline.

## Next docs

- Concepts: `lifecycle`, `transports`, `error-handling`.
- APIs: `constructor`, `do_transaction`, `cancel`, `check_status`.
- Models: `SdkConfig`, `AppToAppConfig`, `TransactionRequest`, `TransactionResult`, `TransactionListener`, `SdkError`.
