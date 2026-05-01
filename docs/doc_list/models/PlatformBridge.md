# Model: `PlatformBridge` (callback interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Host-platform callback bridge for operations only the host language can perform on behalf of the SDK. Today the only such operation is restarting the upstream daemon a transport depends on (used by PADController `restart`).

## Methods

| Name | Signature | Notes |
|---|---|---|
| `restart_upstream_daemon` | `restart_upstream_daemon()` (throws `SdkError`) | Fire-and-forget. Implementations must not block waiting for the daemon. Failures: `TransportUnavailable` (could not even start) or `TransportError` (mid-flight failure). |

## MUST

- Be thread-safe — invoked from the SDK worker thread.
- Surface failures as the documented `SdkError` variants.

## MUST NOT

- Do not block waiting for the daemon to come back online.

## Android-shipping implementation

`com.pinelabs.billing.sdk.AndroidSystemBridge` ships in the AAR as a pre-built `PlatformBridge` implementation that restarts the PADController service via an Android `Intent` (modes: SERVICE / BROADCAST).

## Cross-references

`apis/restart`, `apis/constructor`, `SdkError`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
