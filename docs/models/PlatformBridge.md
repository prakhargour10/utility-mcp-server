# Model: `PlatformBridge` (callback)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Host-platform callback bridge for operations only the host language can perform. Today: restart_upstream_daemon for PADController.

## Methods

| Name | Signature | Notes |
|---|---|---|
| `restart_upstream_daemon` | `[Throws=SdkError] void restart_upstream_daemon()` | Fire-and-forget. Do NOT block waiting for daemon to come back online. |

## MUST

- Implementations must be thread-safe.
- Surface failures as TransportUnavailable (could not start) or TransportError (mid-flight).

## MUST NOT

- Do not block; the SDK will verify recovery via the next transport op.

## Cross-references

`constructor`, `restart`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
