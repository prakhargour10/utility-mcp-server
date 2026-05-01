# JVM — Setup (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** Use the snippets below verbatim. The JVM binding is consumed via the bindings JAR plus the native `cdylib`. There is no Android façade.

## 1. Receive the artifact

You will be sent `jvm-0.5.0-preview.2.zip`. Unpack:

```
jvm-0.5.0-preview.2/
  payload/
    pine-billing-sdk-0.5.0-preview.2.jar
    native/
      linux-x86_64/libuniffi_pine_billing.so
      macos-aarch64/libuniffi_pine_billing.dylib
      macos-x86_64/libuniffi_pine_billing.dylib
      windows-x86_64/uniffi_pine_billing.dll
  README.md
  CHANGELOG.md
  LICENSE.txt
  METADATA.json
  THIRD_PARTY_NOTICES.md
```

## 2. `build.gradle.kts`

```kotlin
plugins {
    kotlin("jvm") version "2.0.20"
}

java {
    toolchain { languageVersion = JavaLanguageVersion.of(17) }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

dependencies {
    implementation(files("libs/pine-billing-sdk-0.5.0-preview.2.jar"))
    implementation("net.java.dev.jna:jna:5.14.0")
    // implementation("com.google.code.gson:gson:2.11.0")  // only if using MasterApp adapter
}
```

## 3. Native lib placement

Place the matching `libuniffi_pine_billing.{so,dylib,dll}` on the JNA search path. The simplest approach during development:

```bash
java -Djna.library.path="$PWD/native/linux-x86_64" -jar your-app.jar
```

For production, package the native lib alongside your app's launch script.

## 4. Construct the SDK

```kotlin
import uniffi.pine_billing.*

val config = SdkConfig(
    defaultTimeoutMs = 60_000u,
    logLevel = null,
    transport = TransportType.CLOUD,
    appToApp = null,                                 // not available on JVM
    applicationId = null,
    cloud = CloudConfig(
        baseUrl = "https://your-cloud-endpoint.example",
        type = CloudType.SANDBOX,
        connectTimeoutMs = 10_000u,
        readTimeoutMs = 30_000u,
    ),
    padController = null,
)

val sdk = PineBillingSdk(config, /*appToAppBridge*/ null, /*platformBridge*/ null)
```

## 5. `Unsigned` helper for Java consumers

UniFFI emits `kotlin.UInt` / `kotlin.ULong`. Java cannot construct these directly. Add this helper to your codebase **once**:

```kotlin
package com.merchant.pos

/**
 * Java interop helper for UniFFI-generated `kotlin.UInt` / `kotlin.ULong` parameters.
 * UniFFI emits these as Kotlin's unsigned types, which Java cannot construct directly.
 * This helper bridges with explicit range checks.
 */
object Unsigned {
    @JvmStatic
    fun toUInt(value: Long): UInt {
        require(value in 0L..0xFFFF_FFFFL) { "value $value does not fit in u32" }
        return value.toInt().toUInt()
    }

    @JvmStatic
    fun toULong(value: Long): ULong {
        require(value >= 0L) { "value $value is negative; cannot be u64" }
        return value.toULong()
    }
}
```

In Java: `Unsigned.toUInt(60_000L)` / `Unsigned.toULong(19_900L)`. Do NOT use `Integers.toUInt` (does not exist) or `kotlin.UInt.constructor-impl` (internal).

## 6. JDK 17 enforcement

`gradle --version` must show JDK 17. Set `org.gradle.java.home` in `~/.gradle/gradle.properties` if your default JDK is older.
