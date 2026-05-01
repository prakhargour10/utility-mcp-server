# Model: `PadControllerConfig` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

PADController transport configuration. One-shot per transaction: a fresh TCP socket is opened to `host:port` for each `do_transaction` and closed after the response is read.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `host` | `string?` | no | Default `"127.0.0.1"`. |
| `port` | `u16?` | no | Default `8082`. |
| `connect_timeout_ms` | `u32?` | no | Default `5_000`. |
| `socket_timeout_ms` | `u32?` | no | Default `245_000`. **Minimum `245_000`** (cardholder PIN entry can take the full window). Lower values raise `InvalidInput`. |

## MUST

- `socket_timeout_ms` must be ≥ 245_000.

## Cross-references

`SdkConfig`, `PadControllerTransactionOptions`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
