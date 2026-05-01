# Concept: versioning-and-support

> **AI INSTRUCTIONS:** Use this file to advise the user on version pinning and migration.

## SDK version (this bundle)

`0.5.0-preview.2` — preview build. Compiles + 180 unit tests pass; not
yet validated against a real Pinelabs terminal at-the-counter.

## Versioning

- SemVer.
- **Pre-1.0 (current — `0.5.0-preview.2`):** breaking changes allowed
  in MINOR bumps. Pin to an exact version in production.
- **Post-1.0:** breaking changes allowed only on MAJOR.

## What is part of the public API

- The UDL (`pine_billing.udl`) — every symbol projected into language
  bindings.
- The thin Kotlin façade in `com.pinelabs.billing.sdk`
  (`PineBillingSdk`, `AndroidSystemBridge`, `MasterAppTransport`).
- `///` doc comments on UDL symbols.

## What is NOT part of the public API

- Adapter-level Rust types.
- Wire formats (CSV column ordering, AppToApp JSON keys,
  PADController frame envelope).
- The `pub(crate)` Rust internals.
- `com.pinelabs.billing.sdk.internal.*` packages.

## Shipping bindings (`0.5.0-preview.2`)

| Binding | Status | Notes |
|---|---|---|
| Android | shipping | AAR; ABIs `arm64-v8a` + `armeabi-v7a` only — **no x86_64** for emulators. minSdk 23 recommended. Runtime deps NOT transitive — consumers must declare `net.java.dev.jna:jna:5.14.0@aar` and `com.google.code.gson:gson:2.11.0`. |
| JVM | shipping | JAR; JNA 5.14+ required at runtime. |
| iOS / Swift | roadmap | not in this release. |
| Python | roadmap | not in this release. |
| Node.js | roadmap | not in this release. |
| C / C++ | roadmap | not in this release. |

## Supported language toolchains

| Language | Floor |
|---|---|
| Kotlin / Android | AGP 8.0+ (AGP 9.0.1+ recommended), Kotlin 1.9+ (2.0.20+ tested), JDK 17, `minSdk` 23, `compileSdk` 36, `targetSdk` 35. Required at consumer runtime: JNA 5.14+ (AAR variant), Gson 2.10+. |
| Kotlin / Java on JVM | JDK 17+, JNA 5.14+. |

## Backward compatibility promises

- `TransactionResult.metadata` keys: stable across releases. New keys
  may be added; existing keys will not be removed without a MAJOR
  bump.
- `PaymentMode` enum: open set. Generated code MUST include a
  default arm.
- `CloudType` enum: open set. Generated code MUST include a
  default arm.

## Migration

When the user upgrades `SDK_VERSION` across a known-breaking
boundary, fetch this doc again and inspect the SDK CHANGELOG
delivered with the artifact.

## Next docs

`overview`, `error-handling`, `distribution`, `binding-aliases`.
