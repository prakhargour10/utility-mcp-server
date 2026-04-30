# Concept: versioning-and-support

> **AI INSTRUCTIONS:** Use this file to advise the user on version pinning and migration.

## Versioning

- SemVer.
- **Pre-1.0 (current):** breaking changes allowed in MINOR bumps. Pin to an exact version in production.
- **Post-1.0:** breaking changes allowed only on MAJOR.

## What is part of the public API

- The UDL (`pine_billing.udl`) — every symbol projected into language bindings.
- `///` doc comments on UDL symbols (these are what get_documentation reflects).

## What is NOT part of the public API

- Adapter-level types (`CloudTransport`, `PadControllerTransport`, etc.).
- Wire formats (CSV column ordering, JSON keys for AppToApp).
- The `pub(crate)` Rust internals.
- Generated UniFFI binding internals (`uniffi.pine_billing.*`).

## MSRV

Rust `1.75`. Frozen until explicitly bumped.

## Supported language toolchains

| Language | Floor |
|---|---|
| Kotlin / Android | AGP 8.0+, Kotlin 1.9+, minSdk 24, compileSdk 34 |
| Swift / iOS | Xcode 15+, Swift 5.9+, iOS 14+ |
| Python | CPython 3.9 – 3.12 |
| Node.js | 18 LTS, 20 LTS |
| C | C11 (gcc 9+, clang 12+, MSVC 2019+) |

## Backward compatibility promises

- `TransactionResult.metadata` keys: stable across releases. New keys may be added; existing keys will not be removed without a MAJOR bump.
- `PaymentMode` enum: open set. Generated code MUST include a default arm.
- `CloudType` enum: open set. Generated code MUST include a default arm.

## Migration

When the user upgrades SDK_VERSION across a known-breaking boundary, fetch this doc again and inspect the SDK CHANGELOG (delivered with the artifact).

## Next docs

`overview`, `error-handling`.
