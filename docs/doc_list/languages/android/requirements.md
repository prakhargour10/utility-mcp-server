# Language: Android — Requirements

> **AI INSTRUCTIONS:** Use this file to validate the user's environment BEFORE generating any setup snippets. Refuse and ask the user if any floor below is unmet.

## Status

✅ **Shipping in 0.5.0-preview.2** as `pine-billing-sdk-0.5.0-preview.2.aar`.

## Operating system / architecture matrix

| ABI | Status |
|---|---|
| `arm64-v8a` | ✓ shipping |
| `armeabi-v7a` | ✓ shipping |
| `x86`, `x86_64` | ✗ not in this release (emulator-only ABIs are not packaged) |

## Toolchain floor

| Tool | Minimum | Notes |
|---|---|---|
| Android Gradle Plugin | 8.0 | namespaces required |
| Kotlin | 1.9 | needed for unsigned-int interop with the UniFFI surface |
| JDK | 17 | required by AGP 8 |
| `compileSdk` | 34 | |
| `minSdk` | 21 | (Android 5.0 Lollipop) |
| `targetSdk` | 33+ | recommended |

## Runtime prerequisites

| Transport | Prerequisite |
|---|---|
| AppToApp | The Pinelabs PoS / MasterApp package installed on the same device. |
| Cloud | `<uses-permission android:name="android.permission.INTERNET" />`. Reachable Cloud `base_url`. |
| PADController | A PADController gateway daemon listening on `127.0.0.1:8082` (or the configured host/port) on the same device. |
| AppToApp on Android 11+ | A `<queries>` block declaring the upstream PoS package — without it `bindService` returns `false` even if the package is installed. |

## NOT required

| Item | Reason |
|---|---|
| `net.java.dev.jna:jna:*` | The AAR loads its native library via `System.loadLibrary("uniffi_pine_billing")` directly. JNA is required only for the JVM binding. |
| Foreground service | Optional. Recommended if a transaction can outlive an Activity (best practice; see `integration.md`). |

## Next docs

`android/setup`, `android/integration`, `android/examples`,
`android/errors`, `android/distribution`,
`concepts/threading`, `concepts/distribution`.
