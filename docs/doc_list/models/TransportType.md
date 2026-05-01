# Model: `TransportType` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

The transport channel used to talk to the terminal.

## Variants

| Name | Notes |
|---|---|
| `AppToApp` | Android-only; binds upstream PoS service per call. |
| `Tcp` | Placeholder in v1 — every method raises `NotSupported`. |
| `Bluetooth` | Routed through the PADController gateway in v1. |
| `Usb` | Routed through the PADController gateway in v1. |
| `Serial` | Routed through the PADController gateway in v1. |
| `Cloud` | HTTPS REST. |

## Cross-references

`SdkConfig`, `concepts/capabilities`, `concepts/transports`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
