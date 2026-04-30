# Model: `TransportType` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Transport channel used to talk to the terminal.

## Values

| Value | Notes |
|---|---|
| `AppToApp` | Android-only Messenger IPC into Pinelabs MasterApp. |
| `Tcp` | Placeholder in v1 — set_transport may raise NotSupported. |
| `Bluetooth` | Routes through PADController. |
| `Usb` | Routes through PADController. |
| `Serial` | Routes through PADController. |
| `Cloud` | HTTPS REST to the Pinelabs upstream. |

## MUST

- Provide the matching sub-config in SdkConfig before set_transport(kind).

## MUST NOT

- Do not change transport mid-transaction.

## Cross-references

`SdkConfig`, `set_transport`, `transports`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
