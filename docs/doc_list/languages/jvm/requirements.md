# Language: JVM (Kotlin / Java) — Requirements

> **AI INSTRUCTIONS:** This binding targets the desktop / server JVM. It is distinct from the Android binding: no Android SDK, no `Context`, no main-thread guard, but JNA IS required.

## Status

✅ **Shipping in 0.5.0-preview.2** as `pine-billing-sdk-0.5.0-preview.2.jar`.

## Operating system / architecture matrix

The JAR bundles native libraries for these targets under
`META-INF/jniLibs/<triple>/`. JNA extracts and `dlopen`s the right
one at runtime.

| OS | Arch | Native triple | Status |
|---|---|---|---|
| Linux | x86_64 | `x86_64-unknown-linux-gnu` | ✓ |
| Linux | aarch64 | `aarch64-unknown-linux-gnu` | ✓ |
| macOS | x86_64 | `x86_64-apple-darwin` | ✓ |
| macOS | arm64 | `aarch64-apple-darwin` | ✓ |
| Windows | x86_64 | `x86_64-pc-windows-msvc` | ✓ |

## Toolchain floor

| Tool | Minimum | Notes |
|---|---|---|
| JDK | 11 | 17+ recommended |
| Kotlin (if used) | 1.9 | required for unsigned-int interop |
| JNA | 5.14 | runtime dependency; mandatory |
| Build tool | Maven 3.6+ or Gradle 7+ | |

## Runtime prerequisites

| Transport | Prerequisite |
|---|---|
| AppToApp | ✗ Android-only. Not available on the JVM binding (no IPC primitive). |
| Cloud | Outbound HTTPS reachability to your Cloud `base_url`. |
| PADController | A PADController gateway daemon listening on TCP loopback (default `127.0.0.1:8082`) on the same host. |

## Required dependencies

| GAV | Why |
|---|---|
| `net.java.dev.jna:jna:5.14.0` (or newer 5.x) | JNA loads the native library out of `META-INF/jniLibs/`. |
| `org.jetbrains.kotlin:kotlin-stdlib:1.9.+` | Required even for pure-Java callers — UniFFI emits Kotlin types (incl. `kotlin.UInt`). |
| `org.jetbrains:annotations:24.+` | Compile-time, used by UniFFI-emitted nullability annotations. |

## NOT applicable

| Item | Reason |
|---|---|
| Android `Context` | The JVM binding has no Android dependency. |
| Main-thread guard | No notion of a UI thread on a generic JVM. The merchant is responsible for threading (see `jvm/integration.md`). |
| `<queries>` manifest | Android-only. |

## Next docs

`jvm/setup`, `jvm/integration`, `jvm/examples`, `jvm/errors`,
`jvm/distribution`.
