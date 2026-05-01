# Android — Setup (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** Use the snippets below verbatim. Do NOT lower `minSdk` to `21`. Do NOT drop `@aar` from the JNA dependency. Do NOT replace Gson with another JSON library — the upstream wire format is hand-tuned for Gson.

## 1. Receive the artifact

You will be sent `android-kotlin-0.5.0-preview.2.zip`. Unpack it to a temp directory:

```
android-kotlin-0.5.0-preview.2/
  payload/
    pine-billing-sdk-0.5.0-preview.2.aar
  README.md
  CHANGELOG.md
  LICENSE.txt
  METADATA.json
  THIRD_PARTY_NOTICES.md
```

Verify the AAR's SHA-256 against the value in `METADATA.json` before installing.

## 2. Place the AAR

```
app/
  libs/
    pine-billing-sdk-0.5.0-preview.2.aar
```

## 3. `app/build.gradle.kts`

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.merchant.pos"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.merchant.pos"
        minSdk = 23                                 // NOT 21 — JNA on Android needs API 23+
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        // Provision the Pinelabs application id from a non-VCS file.
        val pinelabsAppId = (project.findProperty("PINELABS_APP_ID") as String?)
            ?: System.getenv("PINELABS_APP_ID")
            ?: error("PINELABS_APP_ID not set (use ~/.gradle/gradle.properties or env)")
        buildConfigField("String", "PINELABS_APP_ID", "\"$pinelabsAppId\"")
    }

    buildFeatures {
        buildConfig = true                          // required by AGP 8+ for BuildConfig fields
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlin {
        compilerOptions {
            jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
        }
    }

    packaging {
        jniLibs {
            pickFirsts += "**/libc++_shared.so"     // dedup with JNA's copy
        }
    }
}

dependencies {
    implementation(files("libs/pine-billing-sdk-0.5.0-preview.2.aar"))
    implementation("net.java.dev.jna:jna:5.14.0@aar")        // mandatory; @aar variant only
    implementation("com.google.code.gson:gson:2.11.0")        // mandatory
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation(platform("androidx.compose:compose-bom:2024.10.01"))
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
}
```

> **JDK 17 enforcement:** AGP 9 requires JDK 17 for the Gradle worker. Use `gradle --version` to verify; if it shows JDK 11, set `org.gradle.java.home` in `~/.gradle/gradle.properties`.

## 4. `~/.gradle/gradle.properties`

Provision the Pinelabs application id outside source control:

```
PINELABS_APP_ID=1001
```

The sandbox value is `1001`. Production values are issued by your Pinelabs onboarding contact.

## 5. `AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Required to look up the upstream Pinelabs PoS app on Android 11+. -->
    <queries>
        <package android:name="com.pinelabs.masterapp" />
    </queries>

    <application
        android:name=".PineBillingApp"
        android:label="POS"
        android:theme="@style/Theme.Material3.DayNight">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
```

> Confirm `com.pinelabs.masterapp` with your OEM contact before shipping. The package id may differ on partner-OEM devices.

## 6. `PineBillingApp.kt`

```kotlin
package com.merchant.pos

import android.app.Application
import com.pinelabs.billing.sdk.PineBillingSdk
import uniffi.pine_billing.SdkConfig
import uniffi.pine_billing.AppToAppConfig
import uniffi.pine_billing.TransportType

class PineBillingApp : Application() {
    lateinit var sdk: PineBillingSdk
        private set

    override fun onCreate() {
        super.onCreate()
        val config = SdkConfig(
            defaultTimeoutMs = 60_000u,
            logLevel = null,
            transport = TransportType.APP_TO_APP,
            appToApp = AppToAppConfig(userId = "POS-USER", version = "1.0"),
            applicationId = BuildConfig.PINELABS_APP_ID,
            cloud = null,
            padController = null,
        )
        sdk = PineBillingSdk(this, config, /*platformBridge*/ null)
    }
}
```

The SDK is constructed once per process and reused.

## 7. First-build sanity

Run `./gradlew :app:assembleDebug` once. If you see `Unresolved reference: BuildConfig`, recheck `buildConfig = true`. If you see `UnsatisfiedLinkError: libuniffi_pine_billing` at runtime on an emulator, switch to an arm64 image.

See `errors.md` § "First-run sanity check" for the full triage table.
