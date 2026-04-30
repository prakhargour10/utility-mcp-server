# Model: `Terminal` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

A terminal advertised by discover_terminals.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `id` | `string` | yes | Transport-dependent shape: TCP host:port, BT MAC, USB device path, …. |
| `transport` | `TransportType` | yes | Always equals the active transport at discovery time. |
| `display_name` | `string?` | no |  |
| `model` | `string?` | no |  |
| `serial_number` | `string?` | no |  |

## MUST

- Pass the same Terminal back to connect().

## MUST NOT

- Do not construct Terminals by hand for transports that require discovery.

## Cross-references

`discover_terminals`, `connect`, `TransportType`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
