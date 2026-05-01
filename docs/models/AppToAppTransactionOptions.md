# Model: `AppToAppTransactionOptions` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

AppToApp request extras. Mapped to MasterService JSON keys verbatim.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `gst_in` | `string?` | no | → gstIn |
| `gst_brk_up` | `string?` | no | → gstBrkUp |
| `service_id` | `string?` | no | → serviceID |
| `service_mi` | `string?` | no | → serviceMI |
| `is_transit_mode` | `boolean?` | no | → isTransitMode |
| `payment_mode` | `string?` | no | → paymentMode (raw NCMC code) |
| `service_data` | `string?` | no | → serviceData |

## MUST

_(no positive obligations)_

## MUST NOT

_(no anti-patterns)_

## Cross-references

`TransportOptions`, `TransactionRequest`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
