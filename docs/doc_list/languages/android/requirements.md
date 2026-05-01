# Android — Requirements (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** Treat every row in the tables below as hard floors. Do NOT lower any of them when generating Android sample code.

## Toolchain floors

| Tool | Floor | Notes |
|---|---|---|
| Android Gradle Plugin | **9.0.1+** | AGP 8.x configurations differ; see § "AGP 8 vs AGP 9". |
| Kotlin | **2.0.0+** | Required by AGP 9. |
| Gradle | **8.13+** | Bundled with AGP 9. |
| JDK (build) | **17** | AGP 9 enforces JDK 17 for the Gradle worker. |

## Android SDK targets

| Property | Value | Why |
|---|---|---|
| `compileSdk` | **36** | AGP 9 default. |
| `targetSdk` | **35** | Android 15 — current Play target. |
| `minSdk` | **23** | UniFFI's JNA dependency requires API 23+. **NOT 21.** |

## Mandatory runtime dependencies (consumer must declare)

The AAR ships transport adapters and façade classes only. The following are `implementation`-scoped inside the AAR (NOT transitive); the consumer app MUST declare them:

| Coordinate | Why |
|---|---|
| `net.java.dev.jna:jna:5.14.0@aar` | UniFFI Kotlin bindings call the Rust `cdylib` through JNA. **The `@aar` classifier is required** — the plain JAR variant is for desktop JVM and crashes on Android. |
| `com.google.code.gson:gson:2.11.0` | `MasterAppTransport` serialises the AppToApp envelope through Gson. |

## ABIs

The AAR contains:

- `arm64-v8a`
- `armeabi-v7a`

It does **NOT** contain `x86`, `x86_64`. Standard Android emulator images (x86_64) will fail at SDK construction with `UnsatisfiedLinkError: libuniffi_pine_billing`. Use a real arm64 device or an `arm64-v8a` emulator image.

## Native-lib packaging

Add to `android.packaging`:

```kotlin
android {
    packaging {
        jniLibs {
            pickFirsts += "**/libc++_shared.so"
        }
    }
}
```

The Pine SDK and JNA both ship `libc++_shared.so`; without `pickFirsts` the build fails with a duplicate-resource error.

## Compose / `BuildConfig`

If you reference `BuildConfig.PINELABS_APP_ID` (you should — see `integration.md`), AGP 8+ requires:

```kotlin
android {
    buildFeatures {
        buildConfig = true
    }
}
```

Failing to enable this surfaces as `Unresolved reference: BuildConfig` at compile time.

## AGP 8 vs AGP 9

| Concern | AGP 9 (recommended) | AGP 8 (legacy) |
|---|---|---|
| Kotlin JVM target | `kotlin { compilerOptions { jvmTarget = JvmTarget.JVM_17 } }` | `kotlinOptions { jvmTarget = "17" }` |
| Gradle | 8.13+ | 8.7+ |
| Kotlin | 2.0.0+ | 1.9.x ok |

`kotlinOptions { jvmTarget = "17" }` is **invalid on AGP 9** and produces a build-script error.

## ProGuard / R8

The AAR ships `consumer-rules.pro` so apps with R8 enabled need no manual rules. **Known issue (0.5.0-preview.2):** the bundled rule references the wrong UniFFI namespace (`uniffi.pine_billing_sdk.**` instead of `uniffi.pine_billing.**`). See `errors.md` § "ProGuard / R8 stripped UniFFI bindings" for the workaround.

## OEM matrix

Device must be a Pinelabs-flashed Android terminal where the upstream PoS app (`com.pinelabs.masterapp` — confirm with your OEM contact) is installed. Generic Android devices CANNOT run AppToApp transactions.
