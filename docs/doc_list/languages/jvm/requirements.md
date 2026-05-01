# JVM — Requirements (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** The JVM binding is for back-office / server tooling that talks to the Cloud transport (or a future TCP transport). It does NOT support AppToApp — there is no Android `Context` and no upstream PoS service.

## Toolchain floors

| Tool | Floor |
|---|---|
| JDK | **17** (JVM target 17) |
| Kotlin | **2.0.0+** (when consuming from Kotlin) |
| Build tool | Gradle 8+ or Maven 3.9+ |

## Mandatory runtime dependencies

| Coordinate | Why |
|---|---|
| `net.java.dev.jna:jna:5.14.0` | UniFFI Kotlin bindings call the Rust `cdylib` through JNA. **Plain JAR (no `@aar`)** on JVM. |
| `com.google.code.gson:gson:2.11.0` | Required only if you also use the (server-side) MasterApp adapter; safe to omit on a Cloud-only deployment. |

## Native artifact

The JVM distribution ships the `cdylib` next to the bindings JAR for the supported host platforms (Linux x86_64, macOS arm64/x86_64, Windows x86_64). The bindings JAR resolves it via JNA's standard search path.

## Capabilities

| Transport | Available on JVM | Notes |
|---|---|---|
| AppToApp | ✗ | Requires Android `Context` + upstream PoS service. |
| Cloud | ✓ | Primary use case for JVM. |
| PadController | partial | Possible if a `PlutusTransport` daemon is reachable on `127.0.0.1:8082`; not the typical JVM use case. |
| Tcp | ✗ | v1 placeholder. |
