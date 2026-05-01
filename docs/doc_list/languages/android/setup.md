# Language: Android — Setup

> **AI INSTRUCTIONS:** This file is the canonical setup recipe. Do not invent additional dependencies. The AAR does NOT need JNA.

## 1. Drop the AAR into the project

Pinelabs ships the artifact as a direct file drop (no Maven Central
yet). Place it under `app/libs/`:

```
app/libs/pine-billing-sdk-0.5.0-preview.2.aar
```

## 2. `app/build.gradle.kts`

```kotlin
android {
    namespace = "com.merchant.pos"
    compileSdk = 34

    defaultConfig {
        minSdk = 21
        targetSdk = 33
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions { jvmTarget = "17" }

    packaging {
        jniLibs.useLegacyPackaging = false
        // Avoid duplicate libc++_shared.so collisions when other AARs
        // bundle the C++ runtime.
        jniLibs.pickFirsts += setOf("**/libc++_shared.so")
    }
}

dependencies {
    implementation(files("libs/pine-billing-sdk-0.5.0-preview.2.aar"))
    // No JNA dependency — the AAR loads its native lib via
    // System.loadLibrary directly.

    // For coroutine-based dispatch (recommended):
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
```

## 3. `AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Cloud transport: required if you call sdk over the network. -->
    <uses-permission android:name="android.permission.INTERNET" />

    <!--
        AppToApp transport: MANDATORY on Android 11+ (API 30+).
        Without this <queries> block, bindService() returns false even
        if the upstream Pinelabs PoS package is installed.
    -->
    <queries>
        <package android:name="com.pinelabs.masterapp" />
    </queries>

    <application … >
        … your activities …
    </application>
</manifest>
```

If your terminal vendor uses a different upstream package name, replace
`com.pinelabs.masterapp` with the value documented for your terminal.

## 4. ProGuard / R8

```proguard
# UniFFI generated bindings
-keep class uniffi.pine_billing.** { *; }
# Public façade
-keep class com.pinelabs.billing.sdk.** { *; }
# Listener implementations referenced via UniFFI's reflection.
-keepclassmembers class ** implements uniffi.pine_billing.TransactionListener { *; }
-keepclassmembers class ** implements uniffi.pine_billing.TestPrintListener  { *; }
-keepclassmembers class ** implements uniffi.pine_billing.DiscoveryListener  { *; }
-keepclassmembers class ** implements uniffi.pine_billing.PlatformAppToAppBridge { *; }
-keepclassmembers class ** implements uniffi.pine_billing.PlatformBridge { *; }
```

## 5. Imports cheat-sheet

The SDK splits its public surface across two packages — both are
**public**:

| Package | Contains | Import? |
|---|---|---|
| `com.pinelabs.billing.sdk` | `PineBillingSdk` (the façade), `AndroidSystemBridge`, `MasterAppTransport` | ✅ yes |
| `uniffi.pine_billing` | All models, enums, listeners (`SdkConfig`, `TransactionRequest`, `TransactionListener`, `SdkException`, …) | ✅ yes — merchants MUST import models from here |

Anything under `com.pinelabs.billing.sdk.internal.*` is implementation
detail; do NOT import.

## Next docs

`android/integration`, `android/examples`, `android/errors`,
`android/distribution`.
